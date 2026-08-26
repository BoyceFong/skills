#!/usr/bin/env python3
"""把 recommended-skills.json 渲染进 README.md（中文）与 README_EN.md（英文）的标记区间。

recommended-skills.json 是唯一事实源。本脚本只重写两个标记之间的内容：

    <!-- recommended-skills:start -->
    ...
    <!-- recommended-skills:end -->

改完 JSON 后运行：python3 scripts/render_recommended.py
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "recommended-skills.json"
START = "<!-- recommended-skills:start -->"
END = "<!-- recommended-skills:end -->"

CATEGORY_ZH = {"engineering": "工程", "learning": "学习", "quant": "量化"}
CATEGORY_EN = {"engineering": "Engineering", "learning": "Learning", "quant": "Quant"}


def pick(*values):
    """返回第一个非空值，否则返回空字符串。"""
    for v in values:
        if v:
            return v
    return ""


def _md_link(url):
    return f"[{url}]({url})" if url else ""


def source_line(skill, lang):
    """构造「官方来源」行，含可选的 homepage。"""
    source = skill.get("source", "")
    home = skill.get("homepage", "")
    line = _md_link(source)
    if home:
        if lang == "zh":
            extra = f"（文档：{_md_link(home)}）"
        else:
            extra = f" (docs: {_md_link(home)})"
        line = line + extra if line else _md_link(home)
    return line


def install_zh(skill):
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


def install_en(skill):
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
        return ", then ".join(steps)
    if method == "git":
        repo = ins.get("repo", "")
        path = ins.get("path", "")
        if repo and path:
            return f"`git clone {repo}`, then symlink `{path}` to `~/.claude/skills/{name}/`"
        return f"`git clone {repo} ~/.claude/skills/{name}/`"
    if method == "copy":
        return f"Copy/symlink `{name}/SKILL.md` (with `scripts/`, `references/`, etc.) to `~/.claude/skills/{name}/`"
    return "See `recommended-skills.json`"


def _group(skills):
    by_cat = {}
    for s in skills:
        by_cat.setdefault(s.get("category", "other"), []).append(s)
    return by_cat


def render_zh(skills):
    lines = []
    for cat, items in _group(skills).items():
        lines.append(f"### {CATEGORY_ZH.get(cat, cat)}")
        lines.append("")
        for s in items:
            title = pick(s.get("title"), s["name"])
            lines.append(f"#### {title}（`{s['name']}`）")
            lines.append("")
            lines.append(f"- **简介**：{pick(s.get('description'))}")
            lines.append(f"- **官方来源**：{source_line(s, 'zh')}")
            lines.append(f"- **安装**：{install_zh(s)}")
            lines.append(f"- **如何使用**：{pick(s.get('usage'))}")
            if s.get("notes"):
                lines.append(f"- **备注**：{s['notes']}")
            lines.append("")
    return "\n".join(lines).rstrip()


def render_en(skills):
    lines = []
    for cat, items in _group(skills).items():
        lines.append(f"### {CATEGORY_EN.get(cat, cat)}")
        lines.append("")
        for s in items:
            title = pick(s.get("title_en"), s.get("title"), s["name"])
            lines.append(f"#### {title} (`{s['name']}`)")
            lines.append("")
            lines.append(f"- **Description**: {pick(s.get('description_en'), s.get('description'))}")
            lines.append(f"- **Source**: {source_line(s, 'en')}")
            lines.append(f"- **Install**: {install_en(s)}")
            lines.append(f"- **Usage**: {pick(s.get('usage_en'), s.get('usage'))}")
            if s.get("notes_en") or s.get("notes"):
                lines.append(f"- **Note**: {pick(s.get('notes_en'), s.get('notes'))}")
            lines.append("")
    return "\n".join(lines).rstrip()


def inject(path, rendered):
    text = path.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print(f"error: 缺少标记 {START} / {END}：{path}", file=sys.stderr)
        return False
    start_idx = text.index(START) + len(START)
    end_idx = text.index(END)
    new_text = text[:start_idx] + "\n" + rendered + "\n" + text[end_idx:]
    path.write_text(new_text, encoding="utf-8")
    return True


def main():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    skills = data.get("skills", [])
    targets = {
        ROOT / "README.md": render_zh(skills),
        ROOT / "README_EN.md": render_en(skills),
    }
    ok = True
    for path, rendered in targets.items():
        if not path.exists():
            print(f"error: 目标文件不存在：{path}", file=sys.stderr)
            ok = False
            continue
        if inject(path, rendered):
            print(f"已渲染 {len(skills)} 个 skill 到 {path.name}")
        else:
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
