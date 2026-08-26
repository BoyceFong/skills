#!/usr/bin/env python3
"""Diagnose a README against the better-readme patterns.

Usage:
    python3 check_readme.py <path-to-README.md> [--json]

Outputs a checklist of present/missing patterns with a score. This is a
diagnostic aid, not a grade: use judgment about which missing items actually
matter for the project type.
"""

import argparse
import json
import re
import sys
from pathlib import Path


def _headings(text):
    return [ln.strip() for ln in text.splitlines() if re.match(r"^#{1,6}\s+", ln)]


def _fenced_code_blocks(text):
    return re.findall(r"```|~~~", text)


def _count_images(text):
    markdown = len(re.findall(r"!\[[^\]]*\]\([^)]+\)", text))
    html = len(re.findall(r"<img\b", text))
    return markdown + html


def _count_links(text):
    return len(re.findall(r"\[[^\]]+\]\([^)]+\)", text))


def _badges(text):
    # badge images are typically shields.io images near the top
    first_screen = text[:4000]
    markdown = re.findall(
        r"!\[[^\]]*\]\(https?://(?:img\.shields\.io|badgen\.net|github\.com/[^/]+/[^/]+/actions)[^)]*\)",
        first_screen,
    )
    html = re.findall(
        r"<img[^>]+src=\"https?://(?:img\.shields\.io|badgen\.net)[^\"]*\"",
        first_screen,
    )
    return len(markdown) + len(html)


def analyze(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    n_lines = len(lines)
    heads = [re.sub(r"^#+\s*", "", h) for h in _headings(text)]
    heads_lower = " ".join(heads).lower()
    first_screen = "\n".join(lines[:60])
    prose_first = "\n".join(
        ln for ln in lines[:30] if ln.strip() and not ln.lstrip().startswith(("#", "!["))
    )

    checks = []

    def add(pid, label, passed, evidence=""):
        checks.append({"id": pid, "label": label, "passed": bool(passed), "evidence": evidence})

    add("title", "Has a top-level title (# or first line)", bool(lines) and (
        lines[0].startswith("# ") or bool(heads)
    ), lines[0][:80] if lines else "")

    add("pitch", "One-line pitch in first 30 lines",
        any(len(s.strip()) > 30 and len(s.strip()) < 220 for s in prose_first.splitlines()),
        prose_first.splitlines()[0][:120] if prose_first.splitlines() else "")

    add("badges", "Status badges near the top (license/version/CI/community)",
        _badges(text) >= 2, f"{_badges(text)} badge image(s) found")

    add("visual", "Visual proof in first screen (banner/screenshot/chart)",
        _count_images(first_screen) >= 1, f"{_count_images(first_screen)} image(s) in first screen")

    add("toc", "Table of contents (needed past ~100 lines)",
        ("table of contents" in heads_lower) or (n_lines > 100 and bool(
            re.search(r"\[[^\]]+\]\(#", "\n".join(lines[:80]))
        )), f"{n_lines} lines total")

    add("quickstart", "Install / quickstart section",
        any(k in heads_lower for k in ("install", "quickstart", "getting started", "quick start", "usage", "setup", "getting-started")),
        ", ".join(h for h in heads if any(k in h.lower() for k in ("install", "quickstart", "getting started", "quick start", "usage", "setup"))) or "")

    add("code_example", "Runnable code/command example",
        len(_fenced_code_blocks(text)) >= 1, f"{len(_fenced_code_blocks(text))} fenced code block(s)")

    add("expected_output", "Expected output or success signal",
        any(k in first_screen.lower() for k in ("you should see", "output", "expected", "localhost", "=>", "$ ")) or len(_fenced_code_blocks(text)) >= 2,
        "")

    add("docs_link", "Links to deeper documentation",
        any(k in heads_lower or k in text.lower()[:8000] for k in ("documentation", "docs", "manual", "guide", "learn")),
        "")

    add("features", "Features/highlights section",
        any(k in heads_lower for k in ("features", "highlights", "capabilities", "why")),
        "")

    add("evidence", "Evidence (benchmarks, numbers, comparisons)",
        bool(re.search(r"benchmark|faster|times|compare|vs\.|performance|table", text[:12000], re.I)),
        "")

    add("boundaries", "Honest boundaries / limitations / 'why not'",
        any(k in heads_lower or k in text.lower() for k in ("why shouldn't", "limitations", "why not", "not for", "when not to", "tradeoff")),
        "")

    add("faq", "FAQ or common questions",
        any(k in heads_lower for k in ("faq", "questions", "troubleshoot")),
        "")

    add("contributing", "Contributing path",
        bool(re.search(r"contribut", text, re.I)) or "contributing" in heads_lower,
        "")

    add("support", "Support / community channels",
        bool(re.search(r"discord|slack|forum|discussions|chat|stack overflow|support", text, re.I)),
        "")

    add("license", "License stated",
        bool(re.search(r"licen[sc]e", text, re.I)),
        "")

    add("security", "Security policy / vulnerability reporting",
        bool(re.search(r"securit|vulnerab", text, re.I)),
        "")

    passed = sum(1 for c in checks if c["passed"])
    return {
        "path": str(path),
        "lines": n_lines,
        "score": passed,
        "total": len(checks),
        "checks": checks,
    }


def main():
    ap = argparse.ArgumentParser(description="Diagnose a README against better-readme patterns.")
    ap.add_argument("path", help="Path to the README.md file")
    ap.add_argument("--json", action="store_true", help="Emit JSON instead of a human report")
    args = ap.parse_args()

    try:
        result = analyze(args.path)
    except FileNotFoundError:
        print(f"File not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\nREADME diagnostics: {result['path']} ({result['lines']} lines)")
    print(f"Score: {result['score']}/{result['total']}\n")
    for c in result["checks"]:
        mark = "✓" if c["passed"] else "✗"
        line = f"  {mark} {c['label']}"
        if c["evidence"]:
            line += f"  — {c['evidence']}"
        print(line)
    print()


if __name__ == "__main__":
    main()
