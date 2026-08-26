# My Skills

个人 agent skills 收藏库，分两类资产：

- **原创 skills**：源码 vendored 在本仓库 `skills/<分类>/<name>/`，可直接编辑、随 git 版本管理。
- **第三方推荐 skills**：不 vendored 源码，只在 `recommended-skills.json`（机器可读清单）里记录官方来源与安装方式，需要时从上游安装。

## 目录结构

```
.
├── skills/                       # 原创 skills（按分类组织，源码在此）
│   ├── engineering/              # 工程类
│   ├── learning/                 # 学习类
│   └── quant/                    # 量化类
├── recommended-skills.json       # 第三方推荐清单（唯一事实源，机器可读）
├── recommended-skills.md         # 第三方推荐清单（人类可读，由脚本生成）
├── scripts/render_recommended.py # 从 JSON 生成 recommended-skills.md
├── README.md                     # 本文件（人类入口）
├── CLAUDE.md                     # Claude Code 的约定与安装指令
└── AGENTS.md                     # 其他 agent（Codex / Doubao / DeepSeek 等）的约定与安装指令
```

## 快速上手

### 安装原创 skills

原创 skill 位于 `skills/<分类>/<name>/`，是**源码组织**。Claude Code 只自动发现扁平的 `~/.claude/skills/<name>/SKILL.md`，因此需要把每个 skill 摊平安装：

```bash
# 例如把 engineering/better-readme 安装为 ~/.claude/skills/better-readme
ln -s "$PWD/skills/engineering/better-readme" ~/.claude/skills/better-readme
```

其他 agent（Codex / Doubao / DeepSeek 等）按其各自的 skill 机制安装即可，见 `AGENTS.md`。

### 安装第三方推荐 skills

见 [`recommended-skills.md`](./recommended-skills.md)。清单源数据在 `recommended-skills.json`，逐条按其 `install` 字段安装即可。

## 约定

- **原创 vs 第三方分界**：原创 skill 源码提交进 `skills/`；第三方 skill 不提交源码，只更新 `recommended-skills.json`。
- **单一事实源**：`recommended-skills.json` 是权威数据，`recommended-skills.md` 由 `scripts/render_recommended.py` 生成，**不要手改**。
- **新增/修改第三方推荐**：改 `recommended-skills.json` → 运行 `python3 scripts/render_recommended.py` 重新生成 `recommended-skills.md`。

## 清单字段说明

`recommended-skills.json` 中每个条目的字段：

| 字段 | 说明 |
| --- | --- |
| `name` | skill 唯一 id，与 `SKILL.md` 的 `name` 一致 |
| `title` | 人类可读名 |
| `category` | 分类（`engineering` / `learning` / `quant` / 其他） |
| `description` | 一句话简介 |
| `source` | 官方来源（仓库链接） |
| `homepage` | 文档 / 主页（可选） |
| `install` | 安装方式：`method`（`plugin` / `git` / `copy`）+ 对应字段 + 可选 `command` |
| `usage` | 如何使用 / 何时触发 |
| `notes` | 备注（可选） |
