# Annotated examples from the ten source projects

The patterns in `SKILL.md` come from these READMEs. This file shows each pattern in context so you can imitate the *why*, not just the shape.

## 1. One-line pitch (uv, Deno, React)

**uv:**
> An extremely fast Python package and project manager, written in Rust.

**Deno:**
> Deno is a JavaScript, TypeScript, and WebAssembly runtime with secure defaults and a great developer experience. It's built on V8, Rust, and Tokio.

**React:**
> React is a JavaScript library for building user interfaces.

Pattern: subject + what it is + the differentiator, in one sentence. The pitch sits directly under the title, before any marketing.

## 2. Badges in the title line (React, Deno, Zulip)

React puts license, npm version, CI, and "PRs welcome" badges right in the `#` heading line. Deno and Zulip line up badges under the title. These answer "is this project healthy?" in one glance.

## 3. Honest boundaries (ripgrep)

ripgrep has a "Why shouldn't I use ripgrep?" section that names concrete cases where grep or other tools win:

> - There are important corner cases where ripgrep may not be the best tool. For example, ... it does not support multi-line search in a way that replaces pcre2grep ...

Pattern: name the failure cases explicitly. It converts "is this right for me?" from an unanswerable marketing question into a decision the reader can make.

## 4. Evidence with methodology (ripgrep, uv)

ripgrep shows benchmark tables vs. grep/ag/ugrep with exact commands, corpus description, hardware, and the caveat: "a single benchmark is never enough!" uv shows a benchmark chart plus "10-100x faster than pip" with a link to `BENCHMARKS.md`. Numbers without methodology read as hype; with methodology they read as engineering.

## 5. 30-second success path (Deno, TensorFlow)

Deno: six install commands grouped by platform → "Your first Deno program" (a runnable server) → "Learn more" links. The reader goes from "what is this?" to "it works!" in under a minute.

## 6. Visual proof (VS Code, n8n, uv)

VS Code centers a product screenshot in the first screen. n8n shows a banner plus a UI screenshot with a caption. uv uses `<picture>` with `prefers-color-scheme` for dark/light benchmark charts. Captions matter: "Installing Trio's dependencies with a warm cache" tells the story without reading the chart.

## 7. TOC as navigation (freeCodeCamp, Node.js)

freeCodeCamp has a short Table of Contents with anchors; Node.js (900+ lines) has a full TOC covering support, releases, download, security, contributing, and team. build-your-own-x takes it to the extreme: the TOC *is* the document skeleton.

## 8. Reader personas (Zulip, React)

Zulip's "Getting started" splits by role: contributing code, contributing non-code, checking it out, running a server, using the cloud. React's Installation splits by intent: quick taste, add to existing project, start fresh. Every reader finds their shortest path.

## 9. Capability bullets that sell benefits (uv, n8n)

uv's Highlights:
> - A single tool to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv`, and more.
> - 10-100x faster than pip.
> - Installable without Rust or Python via `curl` or `pip`.

n8n's Key Capabilities pairs a bolded capability with one benefit sentence. Each line names the pain it removes.

## 10. License transparency (n8n)

n8n explains its fair-code / Sustainable Use License in plain words with a short "Source Available / Self-Hostable / Extensible" list instead of a bare license link. Non-standard licensing needs plain-language explanation.

## 11. Human touches (build-your-own-x, n8n, Zulip)

- build-your-own-x: a Feynman quote ("What I cannot create, I do not understand").
- n8n: a "What does n8n mean?" section with the founder's own story.
- Zulip: "1500+ contributors merging over 500 commits a month" — concrete community health numbers.

These details turn a repo into something maintained by people.
