# 推荐安装的第三方 skills

> 本文件由 `scripts/render_recommended.py` 从 `recommended-skills.json` 自动生成，勿手改。清单源数据见 [`recommended-skills.json`](./recommended-skills.json)。

## 工程

### Skill Creator（`skill-creator`）

- **简介**：Anthropic 官方技能创作工具，从零创建、修改、评测一个 skill，或优化 description 以提升触发准确率。
- **官方来源**：[https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- **安装**：`claude plugin install skill-creator@claude-plugins-official`
- **如何使用**：当要创建新 skill、改进现有 skill，或跑评测 / 优化触发词时使用。
- **备注**：示例条目，可替换为任意真实第三方 skill。

### PDF（`pdf`）

- **简介**：Anthropic 官方 PDF 技能，读写、分析、转换 PDF 文档。
- **官方来源**：[https://github.com/anthropics/skills](https://github.com/anthropics/skills)（文档：[https://github.com/anthropics/skills/tree/main/skills/pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/anthropics/skills ~/anthropics-skills && ln -s ~/anthropics-skills/skills/pdf ~/.claude/skills/pdf`
- **如何使用**：处理 PDF 文档（读取、生成、提取、转换）时使用。
- **备注**：示例条目，可替换为任意真实第三方 skill。
