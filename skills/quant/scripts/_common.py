"""Shared helpers for quant-autoresearch scripts (internal, not a public API)."""

import hashlib
import re
import shlex
import subprocess
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


RESULTS_HEADER = ["run_tag", "commit", "metric", "status", "description"]

REQUIRED_CONFIG = {
    "project": ["name", "metric", "data_file", "data_version"],
    "experiment": [
        "budget_seconds",
        "timeout_seconds",
        "backtest_cmd",
        "metrics_file",
        "allowed_files",
    ],
    "decision": ["direction", "min_improvement", "min_improvement_abs", "min_t_stat", "constraints"],
    "validation": ["test_fraction"],
}


def load_config(project_dir):
    path = Path(project_dir) / "research.toml"
    if not path.exists():
        raise ValueError(f"no research.toml found in {project_dir}")
    with open(path, "rb") as f:
        cfg = tomllib.load(f)
    errors = []
    for section, keys in REQUIRED_CONFIG.items():
        if section not in cfg:
            errors.append(f"missing section [{section}]")
            continue
        for key in keys:
            if key not in cfg[section]:
                errors.append(f"missing key [{section}].{key}")
    decision = cfg.get("decision", {})
    if decision.get("direction") not in ("higher", "lower"):
        errors.append("[decision].direction must be 'higher' or 'lower'")
    exp = cfg.get("experiment", {})
    if not isinstance(exp.get("allowed_files"), list) or not exp.get("allowed_files"):
        errors.append("[experiment].allowed_files must be a non-empty list")
    if not exp.get("backtest_cmd"):
        errors.append("[experiment].backtest_cmd is empty")
    if cfg.get("project", {}).get("data_version") in (None, "", "UNSET"):
        errors.append("[project].data_version is not pinned (run init_research.py --pin-data)")
    if errors:
        raise ValueError("invalid research.toml:\n  " + "\n  ".join(errors))
    return cfg


def git(project_dir, *args, check=True):
    return subprocess.run(
        ["git", *args],
        cwd=str(project_dir),
        capture_output=True,
        text=True,
        check=check,
    )


def short_hash(project_dir):
    return git(project_dir, "rev-parse", "--short", "HEAD").stdout.strip()


def current_branch(project_dir):
    return git(project_dir, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()


def engine_cmd(config):
    return shlex.split(config["experiment"]["backtest_cmd"])


def read_results(project_dir):
    path = Path(project_dir) / "results.tsv"
    rows = []
    if path.exists():
        for i, line in enumerate(path.read_text().splitlines()):
            if not line.strip():
                continue
            parts = line.split("\t")
            if i == 0 and parts == RESULTS_HEADER:
                continue
            rows.append(dict(zip(RESULTS_HEADER, parts)))
    return rows


def append_result(project_dir, run_tag, commit, metric, status, description):
    path = Path(project_dir) / "results.tsv"
    desc = " ".join(str(description).split())
    if not path.exists():
        path.write_text("\t".join(RESULTS_HEADER) + "\n")
    with open(path, "a") as f:
        f.write("\t".join([run_tag, commit, str(metric), status, desc]) + "\n")


def last_accepted(results):
    for row in reversed(results):
        if row.get("status") in ("baseline", "keep"):
            return row
    return None


def mode_of(config):
    mode = (config.get("mode") or {}).get("name", "explorer")
    return mode if mode in ("explorer", "refiner") else "explorer"


def compute_data_version(data_dir):
    files = sorted(p for p in Path(data_dir).rglob("*") if p.is_file() and p.name != "VERSION")
    h = hashlib.sha256()
    for p in files:
        h.update(p.relative_to(data_dir).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def pin_data(project_dir):
    project = Path(project_dir)
    data_dir = project / "data"
    if not data_dir.exists() or not any(p.is_file() and p.name != "VERSION" for p in data_dir.rglob("*")):
        raise ValueError("no data files found under data/")
    version = compute_data_version(data_dir)
    (data_dir / "VERSION").write_text(version + "\n")
    cfg = project / "research.toml"
    text = cfg.read_text()
    text = re.sub(r'(?m)^data_version\s*=\s*".*"$', f'data_version = "{version}"', text)
    cfg.write_text(text)
    return version
