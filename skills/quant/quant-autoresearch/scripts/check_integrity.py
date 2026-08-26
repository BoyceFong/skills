#!/usr/bin/env python3
"""Static integrity and scope checks for a quant-autoresearch project.

Usage: check_integrity.py <project_dir>

Exit codes: 0 clean, 1 warnings only, 2 hard failures (block the run).
Static checks are heuristics; a passing check does not prove the strategy is leak-free.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as common


HARD_PATTERNS = [
    (r"\bshift\s*\(\s*-", "negative shift (lookahead)"),
    (r"\bpct_change\s*\(\s*-", "negative pct_change (lookahead)"),
    (r"\bdiff\s*\(\s*-", "negative diff (lookahead)"),
    (r"\bbfill\s*\(", "backward fill (lookahead)"),
    (r"\.fillna\s*\(\s*method\s*=\s*['\"]bfill", "bfill fillna (lookahead)"),
    (r"\.iloc\s*\[\s*-", "negative iloc index"),
]

WARN_PATTERNS = [
    (r"\bresample\s*\(", "resample may misalign bars; verify"),
    (r"\.describe\s*\(", "full-sample describe; verify it is not in the signal path"),
    (r"\bdropna\s*\(", "dropna can misalign; verify"),
    (r"\bmerge\s*\(", "merge can introduce future data; verify keys/timing"),
    (r"\brandom\.(seed|Random)|np\.random", "nondeterminism makes runs non-reproducible"),
    (r"\bfill\s*\(", "forward fill in the signal path is often a leak; verify"),
]


def structural_fingerprint(text):
    """Coarse structure fingerprint: imports, def names/signatures, quoted dict keys."""
    imports = sorted(re.findall(r"^(?:import\s+\S+|from\s+\S+\s+import\s+\S+)", text, re.M))
    defs = sorted(re.findall(r"^def\s+(\w+)\s*\(", text, re.M))
    sigs = sorted(re.findall(r"^def\s+[^\n:]+(?=:)", text, re.M))
    keys = sorted(set(re.findall(r'^\s*"([a-zA-Z_][a-zA-Z0-9_]*)"\s*:', text, re.M)))
    return {"imports": imports, "defs": defs, "sigs": sigs, "keys": keys}


def baseline_version(project):
    """Highest archived v<N> dir (skips archive-*), or None."""
    versions = project / "versions"
    nums = []
    if versions.exists():
        for p in versions.glob("v*"):
            if p.name.startswith("archive-"):
                continue
            try:
                nums.append(int(p.name[1:]))
            except ValueError:
                pass
    return versions / f"v{max(nums)}" if nums else None


def run_checks(project):
    fails, warns = [], []
    try:
        config = common.load_config(project)
    except ValueError as e:
        return [str(e)], []

    data_dir = project / "data"
    version_file = data_dir / "VERSION"
    pin = version_file.read_text().strip() if version_file.exists() else ""
    if pin != config["project"]["data_version"]:
        fails.append(
            f"data version mismatch: research.toml={config['project']['data_version']} "
            f"data/VERSION={pin or '(missing)'}"
        )
    data_file = project / config["project"]["data_file"]
    if not data_file.exists():
        fails.append(f"data file missing: {data_file}")

    if not (project / ".git").exists():
        fails.append("not a git repository")
    else:
        changed = common.git(project, "diff", "HEAD", "--name-only").stdout.split()
        allowed = set(config["experiment"]["allowed_files"])
        outside = [f for f in changed if f not in allowed]
        if outside:
            fails.append(f"changes outside allowed files {sorted(allowed)}: {outside}")

    for name in config["experiment"]["allowed_files"]:
        path = project / name
        if not path.exists():
            fails.append(f"allowed file missing: {name}")
            continue
        text = path.read_text(errors="replace")
        if "def generate_signals" not in text:
            fails.append(f"{name} must define generate_signals(df, params)")
        if common.mode_of(config) == "refiner":
            base = baseline_version(project)
            if base is not None and (base / name).exists():
                old = structural_fingerprint((base / name).read_text(errors="replace"))
                new = structural_fingerprint(text)
                for part in ("imports", "defs", "sigs", "keys"):
                    if old[part] != new[part]:
                        fails.append(
                            f"refiner: structural change detected in {name} ({part}); "
                            "only parameter/filter/risk/feature tuning is allowed — switch to explorer for structural work"
                        )
        for pattern, why in HARD_PATTERNS:
            if re.search(pattern, text):
                fails.append(f"{name}: {why}  ({pattern})")
        for pattern, why in WARN_PATTERNS:
            if re.search(pattern, text):
                warns.append(f"{name}: {why}  ({pattern})")
    return fails, warns


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: check_integrity.py <project_dir>")
    project = Path(sys.argv[1]).resolve()
    fails, warns = run_checks(project)
    for w in warns:
        print(f"WARN: {w}")
    for f in fails:
        print(f"FAIL: {f}")
    if not fails and not warns:
        print("integrity checks passed")
    sys.exit(2 if fails else (1 if warns else 0))


if __name__ == "__main__":
    main()
