---
name: better-readme
description: Write, rewrite, or improve a GitHub project README. Use whenever the user asks to create or improve a README, project landing page, repo description, or open-source onboarding docs — even when they don't say "README" explicitly (e.g. "帮我写项目介绍", "make this repo presentable", "我的开源项目没人 star", "把项目包装一下再发 GitHub"). Also use when creating a new repo, preparing a tool for public release, or reviewing whether an existing README is effective. If the user is writing marketing copy, blog posts, or docs site content (not the repo landing page), this skill does not apply.
---

# Better README

## Why this skill exists

The README is the front door of a repository: it decides whether a visitor stays to try the project, becomes a user, or even becomes a contributor. It is the most-read document in almost every open-source project, yet most READMEs are written once and forgotten. This skill encodes the patterns distilled from ten of the most successful open-source projects on GitHub (React, VS Code, ripgrep, uv, Deno, freeCodeCamp, Zulip, n8n, Node.js, build-your-own-x — see `references/examples.md` for annotated excerpts).

The goal is not to produce a template cookie-cutter, but to help you make deliberate choices about structure, emphasis, and honesty so the README earns the reader's time.

## Understand the project before writing

Before writing anything, figure out the answers to these questions. If the answers aren't obvious from the conversation, look at the code, or ask the user — but keep questions to what genuinely changes the README:

1. **What kind of project is this?** A CLI tool, library, framework, app, platform, or learning resource? The README shape differs: a CLI can read like a manpage, a library should be short and link to docs, a platform needs screenshots and capability bullets.
2. **Who is the primary reader?** First-time users, potential contributors, or both? Write the first half for users; put contributor-specific content in a clearly marked section.
3. **What is the one-line value proposition?** If you can't say in one sentence what this project does and why someone should use it over alternatives, the README will fail no matter how pretty it is.
4. **What is the shortest path to "wow"?** Find the single demo/example that takes under a minute and shows the project doing its thing. That becomes the Quickstart centerpiece.
5. **What are the honest limitations?** Every project has tradeoffs. Naming them explicitly builds trust.

## The structure template

Use this skeleton as a default. Adjust order and depth to the project type; the sections marked ★ are non-negotiable for any project with public users.

```
1. ★ Title + one-line pitch + status badges (+ banner/logo)
2. ★ What it is / why it exists (1 short paragraph, maybe 3 bullet "why" points)
3. Visual proof (screenshot, GIF, or benchmark chart — ideally in the first screen)
4. Table of contents (only for READMEs over ~100 lines)
5. ★ Quickstart: install → minimal working example → expected output → next step
6. Features / highlights (organized by reader need, not by implementation detail)
7. Evidence: benchmarks, comparisons, or credible numbers
8. Boundaries & FAQ: what it's NOT for, common questions
9. Documentation & resources (links to real docs, guides, examples)
10. Support & community (chat, forum, issues, discussions)
11. ★ Contributing (a real path in, even if it's just a link to CONTRIBUTING.md)
12. License, security policy, acknowledgements
```

## Section-by-section guidance

### 1. Title, pitch, badges

The first screen must answer, in under 5 seconds: *what is this, is it healthy, and should I care?*

- Keep the title as `# Project Name` or link it to the site (`# [React](https://react.dev/)`).
- Put a **one-line pitch** directly under the title: "uv is an extremely fast Python package and project manager, written in Rust." One sentence, no marketing fluff, no "revolutionary".
- Add 3–6 **badges** near the title: license, latest version, CI status, and one community channel (Discord/Slack/GitHub Discussions). Badges are cheap credibility — they let a stranger verify the project is alive without scrolling.
- If the name is ambiguous, include pronunciation or etymology ("Deno, pronounced dee-no"; "n8n means nodemation").

### 2. What it is / why it exists

One short paragraph: the problem the project solves and for whom. For projects with a design philosophy, three bullets beat a wall of text — React's "Declarative / Component-Based / Learn Once, Write Anywhere" is the gold standard. Each bullet should say *why it matters to the reader*, not just what it is.

### 3. Visual proof

Screenshots, GIFs, or benchmark charts outperform adjectives. Rules:

- Put the most compelling visual in the first screen (VS Code's screenshot, ripgrep's search screenshot).
- Animate what moves (CLI demos) with GIF or asciinema; screenshot what sits still (UIs).
- If the visual is a benchmark, show methodology or link to it — numbers without context read as marketing.
- Consider dark/light variants via `<picture>` and `prefers-color-scheme` (as uv does) if the repo cares about presentation.
- Caption the visual so it tells the story even when the reader only glances at it.

### 4. Table of contents

Long READMEs need a TOC with anchor links. Rule of thumb: past ~100 lines, add one. List the major headings the reader will actually jump to; don't mirror every `####` in the document.

### 5. Quickstart

This is the section that makes or breaks adoption. Structure it as a 30-second success path:

1. **Install** — give the command(s) per platform or package manager. Group them clearly (macOS/Linux, Windows, pip, Homebrew). Link "all installation options" instead of listing every one.
2. **Minimal working example** — the smallest snippet that demonstrates the core value. Copy-paste must work. Show the code and, for CLI tools, the exact command.
3. **Expected output** — show what success looks like (terminal output, screenshot, or a sentence: "You should see…"). This turns "did it work?" from a mystery into a yes/no.
4. **Next step** — one link to the docs or tutorial so the reader knows where to go from here.

Write snippets with a real, complete example — a hello world, a working server, a real file download. Never use placeholder names in the primary example.

### 6. Features / highlights

Organize by *reader need*, not by implementation detail. For each feature, state the benefit. Two good formats:

- **Highlight bullets** (uv): "Replaces pip, pip-tools, pipx, poetry, pyenv, twine, virtualenv and more." — each line names the pain it removes.
- **Capability blocks** (n8n): a bolded capability name followed by one sentence on what it enables.

Keep feature lists scannable: 5–10 items max. Link each major feature to its docs section rather than explaining it fully here.

### 7. Evidence

If the project makes a performance or scale claim, back it with a benchmark table, a credible number, or a link to a dedicated benchmark document. ripgrep's comparison tables against grep/ag/ugrep are the reference example. Include the caveat that a single benchmark isn't conclusive — that honesty makes the data more believable.

### 8. Boundaries & FAQ

Say what the project is *not* for. ripgrep's "Why shouldn't I use ripgrep?" is a masterclass: it names the specific situations (structured text, multi-line fixed patterns, etc.) where another tool wins. This does three things: builds trust, reduces wrong-expectation issues, and pre-empts the "does this do X?" questions. Add a short FAQ for the questions that actually recur (pronunciation, readiness for production, supported platforms).

### 9. Documentation & resources

The README is an entrance, not the destination. Link to the real docs, guides, API reference, and examples. If the docs are large, split the links by audience (users vs. contributors). Keep the README from becoming the documentation — documents rot; links stay fresh.

### 10. Support & community

Give readers a place to ask questions other than the issue tracker: Discord/Slack/GitHub Discussions/forum. List the channels with one-line descriptions of what each is for. Also name the feedback channels (bug reports, feature requests) so people know where to go.

### 11. Contributing

Make the first contribution path embarrassingly easy:

- Link to `CONTRIBUTING.md` or a "How to Contribute" doc with setup and PR workflow.
- Point at "good first issue" labels or first-timers-friendly signals.
- For community projects, state what kinds of non-code contributions are welcome (docs, translations, triage, design).
- Publicly list maintainers/governance if the project is large enough (Node.js's transparency is the reference).

### 12. License, security, acknowledgements

- State the license up front or in the footer, with a link. If it's a non-standard or dual license, explain it in plain words (n8n's fair-code explanation).
- If the project has a security policy, link it from the README (Security.md / vulnerability reporting).
- Credit sponsors, funders, or key influences when relevant — it's good faith and attracts support.

## Principles that override all sections

1. **First screen carries the value.** Every critical decision a reader makes happens above the fold. Pitch, health, and demo visual must all fit there.
2. **Show, don't tell.** A screenshot of output beats "fast and easy". Commands and real output beat adjectives.
3. **Honesty outranks hype.** Limitations, caveats, and "why not this tool" build durable trust. One transparent paragraph is worth ten superlatives.
4. **Length matches the project.** A CLI tool can be as thorough as a manpage (yt-dlp); a small library should be a page and then route to docs; a platform balances marketing and documentation. Aim for the shortest README that still delivers the 30-second success path.
5. **Freshness is a feature.** Keep badges automated, keep version numbers updated, and keep links alive. A README that looks abandoned is abandoned.
6. **Write for skimmers.** Use headers, bullets, tables, and code blocks so the reader can extract value in 30 seconds and dive deeper only where needed.
7. **Details link away.** Anything long-lived (full docs, build instructions, contribution guides) lives in linked files, not in the README.

## Verification

After writing or rewriting a README, verify it with the bundled checker:

```bash
python3 scripts/check_readme.py <path-to-README.md>
```

It reports which patterns are present and which are missing, and prints a score. Treat the output as a diagnostic, not a grade: a missing "security" section is fine for a tiny demo repo, but a missing quickstart is a real problem for any tool that people install. Then do a final read-through asking: *can a stranger go from zero to a successful first run in under a minute, and do they know where to get help?*

## References

- `references/examples.md` — annotated excerpts from the ten source projects, showing each pattern in context.
- `references/checklist.md` — the full checklist used by the checker script, with "why it matters" for each item.
