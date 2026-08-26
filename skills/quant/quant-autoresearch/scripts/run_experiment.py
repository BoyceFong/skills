#!/usr/bin/env python3
"""Run one experiment of a quant-autoresearch loop.

Usage:
  run_experiment.py <project_dir> --baseline --message "baseline"
  run_experiment.py <project_dir> --message "H-3: shorten momentum window"

Mechanics (deterministic, do not bypass):
  1. Scope check: only files in research.toml -> experiment.allowed_files may change.
  2. Integrity check (check_integrity.py): hard failures abort the run.
  3. Commit the change, run the harness (<backtest_cmd> <run_dir>) under timeout.
  4. Read <run_dir>/metrics.json and apply the decision rule from research.toml.
  5. Keep: archive versions/v<N> + git tag v<N>. Discard: git reset --hard to the last accepted
     state (baseline or last keep), so crash-fix commits never survive a rejection.
     Crash: leave the commit in place for fixing forward.
  6. Append one row to results.tsv (never commit results.tsv).

Harness contract: <backtest_cmd> <run_dir> writes <run_dir>/metrics.json with
schema_version 1, primary_metric.value, constraints, optional t_stat, and data_version.
"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as common
import check_integrity


def run_backtest(project, config, run_dir, timeout):
    cmd = common.engine_cmd(config) + [str(run_dir)]
    run_dir.mkdir(parents=True, exist_ok=True)
    timed_out = False
    returncode = None
    with open(run_dir / "run.log", "w") as log:
        proc = subprocess.Popen(cmd, cwd=str(project), stdout=log, stderr=subprocess.STDOUT, text=True)
        try:
            proc.wait(timeout=timeout)
            returncode = proc.returncode
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait()
    return returncode, timed_out


def load_metrics(run_dir, metrics_file, config):
    path = run_dir / metrics_file
    if not path.exists():
        raise ValueError("metrics file not written by harness")
    m = json.loads(path.read_text())
    if m.get("schema_version") != 1:
        raise ValueError(f"schema_version != 1 (got {m.get('schema_version')})")
    pm = m.get("primary_metric")
    if not isinstance(pm, dict) or "value" not in pm:
        raise ValueError("primary_metric.value missing")
    if not isinstance(m.get("constraints"), dict):
        raise ValueError("constraints must be a dict")
    if m.get("data_version") != config["project"]["data_version"]:
        raise ValueError(
            f"data_version mismatch: metrics={m.get('data_version')} "
            f"config={config['project']['data_version']}"
        )
    return m


def raw_metrics(project, run_tag, metrics_file):
    path = project / "experiments" / run_tag / metrics_file
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def gate_reasons(config, metrics):
    reasons = []
    for key, spec in config["decision"]["constraints"].items():
        value = metrics["constraints"].get(key)
        if value is None:
            reasons.append(f"missing constraint metric '{key}'")
            continue
        limit = float(spec["limit"])
        kind = spec.get("kind", "max")
        ok = value <= limit if kind == "max" else value >= limit
        if not ok:
            reasons.append(f"constraint {key}={value} violates {kind} limit {limit}")
    min_t = float(config["decision"]["min_t_stat"])
    if min_t > 0:
        t = metrics.get("t_stat")
        if t is None:
            reasons.append("missing t_stat for significance gate")
        elif float(t) < min_t:
            reasons.append(f"t_stat {t:.2f} < {min_t}")
    return reasons


def calmar_of(metrics):
    aux = metrics.get("auxiliary") or {}
    cons = metrics.get("constraints") or {}
    ann = aux.get("annual_return")
    dd = cons.get("max_drawdown")
    if isinstance(ann, (int, float)) and isinstance(dd, (int, float)) and dd:
        return ann / dd
    return None


def decide(config, base_value, metrics):
    direction = config["decision"]["direction"]
    min_rel = float(config["decision"]["min_improvement"])
    min_abs = float(config["decision"]["min_improvement_abs"])
    new = float(metrics["primary_metric"]["value"])
    base = float(base_value)
    required = max(min_rel * abs(base), min_abs)
    improved = (new - base) >= required if direction == "higher" else (new - base) <= -required
    reasons = []
    if not improved:
        reasons.append(f"{metrics['primary_metric']['name']} {base:.4f} -> {new:.4f} (needed delta {required:+.4f})")
    reasons += gate_reasons(config, metrics)
    if reasons:
        return "discard", "; ".join(reasons)
    return "keep", ""


def decide_refiner(config, base_metrics, metrics, diff_stats):
    """Refiner gate: constraints + Pareto dominance + complexity penalty."""
    direction = config["decision"]["direction"]
    reasons = gate_reasons(config, metrics)
    if reasons:
        return "discard", "; ".join(reasons)
    ref = (config.get("mode") or {}).get("refiner", {})
    eps = float(ref.get("eps", 0.005))
    complexity_lines = int(ref.get("complexity_lines", 15))
    pm_new = float(metrics["primary_metric"]["value"])
    pm_base = float(base_metrics["primary_metric"]["value"])

    base_aux = base_metrics.get("auxiliary") or {}
    new_aux = metrics.get("auxiliary") or {}
    criteria = [
        ("sharpe", direction, pm_base, pm_new),
        ("calmar", "higher", calmar_of(base_metrics), calmar_of(metrics)),
        (
            "max_drawdown",
            "lower",
            (base_metrics.get("constraints") or {}).get("max_drawdown"),
            (metrics.get("constraints") or {}).get("max_drawdown"),
        ),
        (
            "train_primary",
            "higher",
            base_aux.get("train_primary", base_aux.get("train_sharpe")),
            new_aux.get("train_primary", new_aux.get("train_sharpe")),
        ),
    ]
    improved_any = False
    for name, kind, b, n in criteria:
        if not isinstance(b, (int, float)) or not isinstance(n, (int, float)):
            continue
        tol = eps * abs(b) if b else eps
        if kind == "higher":
            if n < b - tol:
                reasons.append(f"pareto {name}: {b:.4f} -> {n:.4f} degrades")
            elif n > b + tol:
                improved_any = True
        else:
            if n > b + tol:
                reasons.append(f"pareto {name}: {b:.4f} -> {n:.4f} degrades")
            elif n < b - tol:
                improved_any = True
    if not reasons and not improved_any:
        reasons.append("pareto: no strict improvement across criteria")

    min_rel = float(config["decision"]["min_improvement"])
    min_abs = float(config["decision"]["min_improvement_abs"])
    required = max(min_rel * abs(pm_base), min_abs)
    gained = (pm_new - pm_base) if direction == "higher" else (pm_base - pm_new)
    added, removed = (diff_stats or (0, 0))
    if gained < required and added + removed > complexity_lines:
        reasons.append(
            f"complexity penalty: gain {gained:+.4f} < required {required:+.4f} with diff {added}+{removed} lines"
        )
    if reasons:
        return "discard", "; ".join(reasons)
    return "keep", ""


def archive(project, n, run_dir, description):
    snap = project / "versions" / f"v{n}"
    snap.mkdir(parents=True, exist_ok=True)
    shutil.copy2(project / "strategy.py", snap / "strategy.py")
    shutil.copy2(project / "research.toml", snap / "research.toml")
    shutil.copy2(run_dir / "metrics.json", snap / "metrics.json")
    (snap / "DESCRIPTION.txt").write_text(description)
    print(f"archived versions/v{n}")


def next_version(project):
    versions = project / "versions"
    nums = []
    if versions.exists():
        for p in versions.glob("v*"):
            try:
                nums.append(int(p.name[1:]))
            except ValueError:
                pass
    return max(nums) + 1 if nums else 1


def main():
    ap = argparse.ArgumentParser(description="Run one quant-autoresearch experiment")
    ap.add_argument("project_dir")
    ap.add_argument("--baseline", action="store_true", help="first run with no code changes")
    ap.add_argument("--message", default="", help="hypothesis / change description")
    ap.add_argument("--budget", type=int, default=None, help="override budget seconds")
    ap.add_argument("--timeout", type=int, default=None, help="override timeout seconds")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    config = common.load_config(project)
    if args.budget:
        config["experiment"]["budget_seconds"] = args.budget
    if args.timeout:
        config["experiment"]["timeout_seconds"] = args.timeout
    timeout = int(config["experiment"]["timeout_seconds"])
    if timeout < int(config["experiment"]["budget_seconds"]):
        sys.exit("timeout_seconds must be >= budget_seconds")
    if not (project / ".git").exists():
        sys.exit("not a git repository; run init_research.py first")
    branch = common.current_branch(project)
    if not branch.startswith("autoresearch/"):
        print(f"WARN: not on an autoresearch/* branch (current: {branch})")

    metrics_file = config["experiment"]["metrics_file"]
    results = common.read_results(project)

    if args.baseline:
        if any(r["status"] in ("baseline", "keep") for r in results):
            sys.exit("baseline already exists")
        changed = common.git(project, "diff", "HEAD", "--name-only").stdout.split()
        if changed:
            sys.exit(f"worktree has changes; baseline must run on the clean scaffold: {changed}")
        run_dir = project / "experiments" / "baseline"
        returncode, timed_out = run_backtest(project, config, run_dir, timeout)
        if timed_out or returncode != 0:
            sys.exit(f"baseline run failed (timeout={timed_out}, exit={returncode}); check {run_dir}/run.log")
        try:
            metrics = load_metrics(run_dir, metrics_file, config)
        except ValueError as e:
            sys.exit(f"baseline metrics invalid: {e}")
        archive(project, 0, run_dir, args.message or "baseline")
        common.git(project, "add", "versions/v0")
        common.git(project, "commit", "-m", "baseline archive v0")
        common.git(project, "tag", "v0")
        commit = common.short_hash(project)
        common.append_result(project, "baseline", commit, metrics["primary_metric"]["value"], "baseline", args.message or "baseline")
        print(f"baseline established: {metrics['primary_metric']} (commit {commit}, tag v0)")
        return

    if not args.message:
        sys.exit("--message is required for experiments")

    pre = common.short_hash(project)
    changed = common.git(project, "diff", "HEAD", "--name-only").stdout.split()
    allowed = set(config["experiment"]["allowed_files"])
    outside = [f for f in changed if f not in allowed]
    if outside:
        sys.exit(f"changes outside allowed files {sorted(allowed)}: {outside}")
    changed_allowed = [f for f in changed if f in allowed]
    if not changed_allowed:
        sys.exit("no changes in allowed files to test")

    fails, warns = check_integrity.run_checks(project)
    for w in warns:
        print(f"WARN: {w}")
    if fails:
        sys.exit("integrity hard failures:\n  " + "\n  ".join(fails))

    base = common.last_accepted(results)
    if base is None:
        sys.exit("no baseline yet; run with --baseline first")

    common.git(project, "add", *changed_allowed)
    common.git(project, "commit", "-m", args.message)
    commit = common.short_hash(project)

    tag = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    run_dir = project / "experiments" / tag
    returncode, timed_out = run_backtest(project, config, run_dir, timeout)
    if timed_out or returncode != 0:
        reason = "timeout" if timed_out else f"exit {returncode}"
        common.append_result(project, tag, commit, 0.0, "crash", f"{args.message}; {reason}")
        print(f"CRASH ({reason}): commit {commit} left in place; fix and re-run")
        return
    try:
        metrics = load_metrics(run_dir, metrics_file, config)
    except (ValueError, json.JSONDecodeError) as e:
        common.append_result(project, tag, commit, 0.0, "crash", f"{args.message}; invalid metrics: {e}")
        print(f"CRASH (invalid metrics: {e}): commit {commit} left in place")
        return

    diff_stats = (0, 0)
    try:
        numstat = common.git(project, "diff", "--numstat", f"{pre}..HEAD", "--", *changed_allowed).stdout.strip()
        if numstat:
            parts = numstat.split()
            diff_stats = (int(parts[0]), int(parts[1]))
    except Exception:
        pass

    mode = common.mode_of(config)
    if mode == "refiner":
        base_metrics = raw_metrics(project, base["run_tag"], metrics_file)
        if base_metrics is None:
            print("WARN: refiner mode but baseline metrics missing; falling back to single-metric rule")
            status, why = decide(config, base["metric"], metrics)
        else:
            status, why = decide_refiner(config, base_metrics, metrics, diff_stats)
    else:
        status, why = decide(config, base["metric"], metrics)
    if status == "keep":
        n = next_version(project)
        archive(project, n, run_dir, args.message)
        common.git(project, "add", f"versions/v{n}")
        common.git(project, "commit", "--amend", "--no-edit")
        commit = common.short_hash(project)
        common.git(project, "tag", f"v{n}")
        print(f"KEEP  {metrics['primary_metric']} -> versions/v{n} (tag v{n})")
    else:
        reset_target = common.last_accepted(common.read_results(project))["commit"]
        common.git(project, "reset", "--hard", reset_target)
        print(f"DISCARD {metrics['primary_metric']} [{why}]")
    common.append_result(project, tag, commit, metrics["primary_metric"]["value"], status, args.message + (f" [{why}]" if status == "discard" else ""))


if __name__ == "__main__":
    main()
