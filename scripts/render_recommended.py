#!/usr/bin/env python3
"""从 recommended-skills.json 生成 recommended-skills.md（人类可读，中文）。

recommended-skills.json 是唯一事实源。运行：python3 scripts/render_recommended.py
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "recommended-skills.json"
OUT = ROOT / "recommended-skills.md"

CATEGORY_ZH = {"engineering": "工程", "learning": "学习", "quant": "量化"}


def pick(*values):
    for v in values:
        if v:
            return v
    return ""


def md_link(url):
    return f"[{url}]({url})" if url else ""


def source_line(skill):
    source = skill.get("source", "")
    home = skill.get("homepage", "")
    line = md_link(source)
    if home:
        extra = f"（文档：{md_link(home)}）"
        line = line + extra if line else md_link(home)
    return line


def install(skill):
    ins = skill.get("install") or {}
    if ins.get("command"):
        return f"`{ins['command']}`"
    method = ins.get("method")
    name = skill["name"]
    if method == "plugin":
        marketplace = ins.get("marketplace", "")
        plugin = ins.get("plugin", name)
        steps = []
        if marketplace:
            steps.append(f"`claude plugin marketplace add {marketplace}`")
        pin = f"{plugin}@{marketplace}" if marketplace else plugin
        steps.append(f"`claude plugin install {pin}`")
        return "，然后 ".join(steps)
    if method == "git":
        repo = ins.get("repo", "")
        path = ins.get("path", "")
        if repo and path:
            return f"`git clone {repo}` 后，把 `{path}` 软链到 `~/.claude/skills/{name}/`"
        return f"`git clone {repo} ~/.claude/skills/{name}/`"
    if method == "copy":
        return f"把 `{name}/SKILL.md`（含 `scripts/`、`references/` 等）复制/软链到 `~/.claude/skills/{name}/`"
    return "见 `recommended-skills.json`"


def render(skills):
    lines = [
        "# 推荐安装的第三方 skills",
        "",
        "> 本文件由 `scripts/render_recommended.py` 从 `recommended-skills.json` 自动生成，勿手改。清单源数据见 [`recommended-skills.json`](./recommended-skills.json)。",
        "",
    ]
    by_cat = {}
    for s in skills:
        by_cat.setdefault(s.get("category", "other"), []).append(s)
    for cat, items in by_cat.items():
        lines.append(f"## {CATEGORY_ZH.get(cat, cat)}")
        lines.append("")
        for s in items:
            title = pick(s.get("title"), s["name"])
            lines.append(f"### {title}（`{s['name']}`）")
            lines.append("")
            lines.append(f"- **简介**：{pick(s.get('description'))}")
            lines.append(f"- **官方来源**：{source_line(s)}")
            lines.append(f"- **安装**：{install(s)}")
            lines.append(f"- **如何使用**：{pick(s.get('usage'))}")
            if s.get("notes"):
                lines.append(f"- **备注**：{s['notes']}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    skills = data.get("skills", [])
    OUT.write_text(render(skills), encoding="utf-8")
    print(f"已渲染 {len(skills)} 个 skill 到 {OUT.name}")


if __name__ == "__main__":
    main()
