# My Skills

个人 Claude Code skills 收藏库，分两类资产：

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
├── scripts/render_recommended.py # 从 JSON 生成下方推荐列表
├── README.md                     # 本文件（中文，人类可读）
├── README_EN.md                  # 英文版
└── CLAUDE.md                     # 给 agent 的约定与安装指令
```

## 快速上手

### 安装原创 skills

原创 skill 位于 `skills/<分类>/<name>/`，是**源码组织**。Claude Code 只自动发现扁平的 `~/.claude/skills/<name>/SKILL.md`，因此需要把每个 skill 摊平安装：

```bash
# 例如把 engineering/better-readme 安装为 ~/.claude/skills/better-readme
ln -s "$PWD/skills/engineering/better-readme" ~/.claude/skills/better-readme
```

### 安装第三方推荐 skills

见下方「推荐安装的第三方 skills」。清单源数据在 `recommended-skills.json`，逐条按其 `install` 字段安装即可。

## 约定

- **原创 vs 第三方分界**：原创 skill 源码提交进 `skills/`；第三方 skill 不提交源码，只更新 `recommended-skills.json`。
- **单一事实源**：`recommended-skills.json` 是权威数据，下方列表由 `scripts/render_recommended.py` 生成，**不要手改列表本身**。
- **新增/修改第三方推荐**：改 `recommended-skills.json` → 运行 `python3 scripts/render_recommended.py` 重新生成 README.md / README_EN.md。

## 推荐安装的第三方 skills

<!-- recommended-skills:start -->
### 工程

#### Skill Creator（`skill-creator`）

- **简介**：Anthropic 官方技能创作工具，从零创建、修改、评测一个 skill，或优化 description 以提升触发准确率。
- **官方来源**：[https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- **安装**：`claude plugin install skill-creator@claude-plugins-official`
- **如何使用**：当要创建新 skill、改进现有 skill，或跑评测 / 优化触发词时使用。
- **备注**：示例条目，可替换为任意真实第三方 skill。

#### PDF（`pdf`）

- **简介**：Anthropic 官方 PDF 技能，读写、分析、转换 PDF 文档。
- **官方来源**：[https://github.com/anthropics/skills](https://github.com/anthropics/skills)（文档：[https://github.com/anthropics/skills/tree/main/skills/pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/anthropics/skills ~/anthropics-skills && ln -s ~/anthropics-skills/skills/pdf ~/.claude/skills/pdf`
- **如何使用**：处理 PDF 文档（读取、生成、提取、转换）时使用。
- **备注**：示例条目，可替换为任意真实第三方 skill。
<!-- recommended-skills:end -->

## 清单字段说明

`recommended-skills.json` 中每个条目的字段：

| 字段 | 说明 |
| --- | --- |
| `name` | skill 唯一 id，与 `SKILL.md` 的 `name` 一致 |
| `title` / `title_en` | 人类可读名（中文 / 英文，`*_en` 可省略） |
| `category` | 分类（`engineering` / `learning` / `quant` / 其他） |
| `description` / `description_en` | 一句话简介 |
| `source` | 官方来源（仓库链接） |
| `homepage` | 文档 / 主页（可选） |
| `install` | 安装方式：`method`（`plugin` / `git` / `copy`）+ 对应字段 + 可选 `command` |
| `usage` / `usage_en` | 如何使用 / 何时触发 |
| `notes` / `notes_en` | 备注（可选） |
