#!/usr/bin/env python3
"""Scaffold a self-driving quant research project for quant-autoresearch.

Usage:
  init_research.py <project_dir> [--name NAME] [--metric sharpe]
                   [--direction higher] [--budget 300] [--engine-cmd "python backtest.py"]
                   [--mode explorer|refiner] [--sample-data] [--pin-data] [--skip-git]

--sample-data generates a deterministic synthetic price series so the project runs out of the box
(smoke tests only; use real point-in-time data for actual research).
"""

import argparse
import random
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as common


TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "assets" / "project-template"


def fill_tokens(path, mapping):
    text = path.read_text()
    for key, value in mapping.items():
        text = text.replace(key, value)
    path.write_text(text)


def generate_sample_data(path, days=2600, seed=7):
    """Deterministic synthetic close series with weak momentum persistence (stdlib only)."""
    rng = random.Random(seed)
    prev = 0.0
    close = 100.0
    day = date(2014, 1, 1)
    lines = ["date,close,volume"]
    written = 0
    while written < days:
        if day.weekday() < 5:
            noise = rng.gauss(0.0, 0.01)
            prev = 0.08 * prev + noise + 0.0004
            close *= 1.0 + prev
            lines.append(f"{day.isoformat()},{close:.6f},{rng.randint(1_000_000, 5_000_000)}")
            written += 1
        day += timedelta(days=1)
    path.write_text("\n".join(lines) + "\n")


def git_init_and_branch(project):
    common.git(project, "init", check=False)
    # Project-local identity fallback so scaffolding works without global git config.
    if common.git(project, "config", "user.email", check=False).returncode != 0:
        common.git(project, "config", "user.name", "quant-autoresearch")
        common.git(project, "config", "user.email", "autoresearch@local")
    common.git(project, "add", "-A")
    common.git(project, "commit", "-m", "scaffold quant-autoresearch project")
    base = date.today().strftime("%Y%m%d")
    branch = f"autoresearch/{base}"
    n = 1
    while common.git(project, "rev-parse", "--verify", branch, check=False).returncode == 0:
        branch = f"autoresearch/{base}-{n}"
        n += 1
    common.git(project, "checkout", "-b", branch)
    return branch


def main():
    ap = argparse.ArgumentParser(description="Scaffold a quant-autoresearch project")
    ap.add_argument("project_dir")
    ap.add_argument("--name", default=None, help="project name (default: directory name)")
    ap.add_argument("--metric", default="sharpe", help="primary metric (default: sharpe)")
    ap.add_argument("--direction", default="higher", choices=["higher", "lower"])
    ap.add_argument("--budget", type=int, default=300, help="per-experiment budget seconds")
    ap.add_argument("--engine-cmd", default="python backtest.py", help="backtest engine command")
    ap.add_argument("--mode", default="explorer", choices=["explorer", "refiner"])
    ap.add_argument("--sample-data", action="store_true", help="generate synthetic sample data")
    ap.add_argument("--pin-data", action="store_true", help="hash data/ and update research.toml")
    ap.add_argument("--skip-git", action="store_true", help="do not initialize git")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()

    if args.pin_data:
        if not (project / "research.toml").exists():
            sys.exit(f"not a quant-autoresearch project: {project}")
        version = common.pin_data(project)
        print(f"data pinned: {version}")
        return

    if project.exists() and any(project.iterdir()) and not (project / "research.toml").exists():
        sys.exit(f"directory not empty and not a quant-autoresearch project: {project}")
    project.mkdir(parents=True, exist_ok=True)
    shutil.copytree(TEMPLATE_DIR, project, dirs_exist_ok=True)

    name = args.name or re.sub(r"[^a-z0-9-]+", "-", project.name.lower()).strip("-") or "quant-research"
    version = "UNSET"
    if args.sample_data:
        data_path = project / "data" / "prices.csv"
        data_path.parent.mkdir(parents=True, exist_ok=True)
        generate_sample_data(data_path)
        version = common.pin_data(project)
    else:
        (project / "data").mkdir(parents=True, exist_ok=True)
        if any(p.is_file() and p.name != "VERSION" for p in (project / "data").rglob("*")):
            version = common.pin_data(project)
        else:
            (project / "data" / "VERSION").write_text("UNSET\n")

    mapping = {
        "__NAME__": name,
        "__METRIC__": args.metric,
        "__DIRECTION__": args.direction,
        "__BUDGET__": str(args.budget),
        "__TIMEOUT__": str(args.budget * 2),
        "__ENGINE_CMD__": args.engine_cmd,
        "__DATA_VERSION__": version,
        "__MODE__": args.mode,
    }
    fill_tokens(project / "research.toml", mapping)
    fill_tokens(project / "AGENTS.md", {"__MODE__": args.mode})
    fill_tokens(project / "pyproject.toml", {"__NAME__": name})

    branch = None
    if not args.skip_git:
        branch = git_init_and_branch(project)

    print(f"created quant-autoresearch project at {project}")
    print(f"  name={name} metric={args.metric} direction={args.direction} budget={args.budget}s")
    if branch:
        print(f"  git branch: {branch}")
    print("next steps:")
    print(f"  1. {project}/.venv/bin/pip install -e .   (or uv sync)  # project deps")
    print("  2. sanity-run the harness manually to confirm the engine command")
    print("  3. python scripts/run_experiment.py <project> --baseline --message \"baseline\"")
    print("  4. start the loop: edit strategy.py, then run_experiment.py --message <hypothesis>")


if __name__ == "__main__":
    main()
