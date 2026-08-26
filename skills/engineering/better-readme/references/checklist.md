# README Checklist

The checklist behind `scripts/check_readme.py`, with the *why* for each item.

## Front matter (first screen)

- [ ] **Title** — a clear `# Project Name`, optionally linking to the project site.
- [ ] **One-line pitch** — one sentence saying what it is and what it does. If the reader can't repeat it back, rewrite it.
- [ ] **Badges (2–6)** — license, version, CI, one community channel. They answer "is this alive and maintained?" without the reader scrolling.
- [ ] **Visual proof** — banner, screenshot, GIF, or benchmark chart. Place it high; it is the fastest form of comprehension.
- [ ] **Pronunciation/etymology** (if the name is unusual) — removes a tiny but real barrier ("how do I say this?").

## Structure

- [ ] **Table of contents** once the README passes ~100 lines, with working anchor links.
- [ ] **Quickstart** — install → minimal working example → expected output → next step.
- [ ] **Features/highlights** — organized by reader benefit, 5–10 scannable items, each linked to docs.
- [ ] **Evidence** — benchmark table, credible numbers, or a link to a benchmark doc for any performance claim.
- [ ] **Boundaries** — explicitly state what the project is not for, or what it doesn't do.
- [ ] **FAQ** — recurring questions answered in place (readiness, platforms, pronunciation, alternatives).

## Links & community

- [ ] **Docs links** — README is the entrance; full documentation lives elsewhere and is linked.
- [ ] **Support channel** — at least one place to ask questions other than the issue tracker.
- [ ] **Contributing path** — a link to CONTRIBUTING.md or a "How to Contribute" section; ideally a pointer to good-first-issues.
- [ ] **Feedback channels** — where to report bugs and request features.

## Trust & maintenance

- [ ] **License** stated with a link; explain non-standard licenses in plain words.
- [ ] **Security policy** linked when the project is large or security-sensitive.
- [ ] **Sponsors/acknowledgements** when relevant.
- [ ] **Freshness** — badges are automated, version numbers correct, links live, no "TODO" placeholders.

## Final read-through questions

1. Can a stranger go from zero to a successful first run in under a minute?
2. Does the first screen (without scrolling) explain what this is and why it matters?
3. Would a reader who never scrolls past the quickstart still know where to get help?
4. Is anything in the README already contradicted by the actual project state (version, commands, screenshots)?
5. Does the length match the project type — no more, no less?
