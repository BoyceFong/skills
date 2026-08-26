#!/usr/bin/env python3
"""Start a new research campaign milestone: archive the old one and reset the ledger.

Usage:
  milestone.py <project_dir> --message "<reason>"

Behavior:
- Requires research.toml and a git repo; the worktree must have no tracked changes.
- Tags the current state as milestone/<YYYYMMDD-HHMMSS>.
- Archives results.tsv into experiments/milestone-<tag>/results-archive.tsv and starts a fresh
  ledger (header only), so the next step is re-running the baseline.
- Moves existing versions/v* into versions/archive-<tag>/ and deletes the old v* git tags (the
  milestone tag keeps the archived state reachable), so the new campaign can mint v0/v1... again.
- Appends a durable, committed record to docs/milestones.md (created if missing).
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as common


def main():
    ap = argparse.ArgumentParser(description="Start a new research campaign milestone")
    ap.add_argument("project_dir")
    ap.add_argument("--message", required=True, help="reason for the milestone (e.g. data re-scope)")
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    if not (project / "research.toml").exists():
        sys.exit(f"not a quant-autoresearch project: {project}")
    if not (project / ".git").exists():
        sys.exit("not a git repository; milestones need git tags")
    changed = common.git(project, "diff", "HEAD", "--name-only").stdout.split()
    if changed:
        sys.exit(f"worktree has tracked changes; commit or revert first: {changed}")

    config = common.load_config(project)
    rows = common.read_results(project)
    last = common.last_accepted(rows)
    tag = datetime.now().strftime("%Y%m%d-%H%M%S")
    tag_name = f"milestone/{tag}"

    common.git(project, "tag", tag_name)

    # Archive old version dirs + free the v<N> tag namespace for the new campaign.
    versions = project / "versions"
    if versions.exists():
        old = sorted(versions.glob("v*"))
        if old:
            archive_versions = versions / f"archive-{tag}"
            archive_versions.mkdir(parents=True, exist_ok=True)
            for p in old:
                shutil.move(str(p), str(archive_versions / p.name))
            common.git(project, "add", "-A")
            for t in common.git(project, "tag", "--list", "v*").stdout.split():
                common.git(project, "tag", "-d", t)

    # Archive the old ledger and start a fresh one.
    archive_dir = project / "experiments" / f"milestone-{tag}"
    archive_dir.mkdir(parents=True, exist_ok=True)
    ledger = project / "results.tsv"
    if ledger.exists():
        shutil.copy2(ledger, archive_dir / "results-archive.tsv")
    ledger.write_text("\t".join(common.RESULTS_HEADER) + "\n")

    # Durable record in committed docs/milestones.md.
    docs = project / "docs"
    docs.mkdir(parents=True, exist_ok=True)
    milestones = docs / "milestones.md"
    if not milestones.exists():
        milestones.write_text(
            "# Milestones\n\n"
            "| tag | date | reason | data_version | best_before |\n"
            "|---|---|---|---|---|\n"
        )
    best_before = f"{last['metric']} ({last['run_tag']})" if last else "—"
    with open(milestones, "a") as f:
        f.write(
            f"| `{tag_name}` | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
            f"{args.message} | `{config['project']['data_version']}` | {best_before} |\n"
        )
    common.git(project, "add", "docs/milestones.md")
    common.git(project, "commit", "-m", f"milestone: {args.message}")

    print(f"milestone {tag_name} created (tag: {tag_name})")
    print(f"ledger archived to {archive_dir / 'results-archive.tsv'}; fresh ledger started")
    if versions.exists() and any(versions.glob("archive-*")):
        print(f"old versions archived under {versions / f'archive-{tag}'}; v* tags cleaned")
    print(f"record appended to {milestones}")
    print("next step: re-run the baseline (run_experiment.py --baseline) and start a new campaign")


if __name__ == "__main__":
    main()
