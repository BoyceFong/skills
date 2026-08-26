# 推荐安装的第三方 skills

> 本文件由 `scripts/render_recommended.py` 从 `recommended-skills.json` 自动生成，勿手改。清单源数据见 [`recommended-skills.json`](./recommended-skills.json)。

## 工程

### Skill Creator（`skill-creator`）

- **简介**：Anthropic 官方技能创作工具，从零创建、修改、评测一个 skill，或优化 description 以提升触发准确率。
- **官方来源**：[https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- **安装**：`claude plugin install skill-creator@claude-plugins-official`
- **如何使用**：当要创建新 skill、改进现有 skill，或跑评测 / 优化触发词时使用。

### PDF（`pdf`）

- **简介**：Anthropic 官方 PDF 技能，读写、分析、转换 PDF 文档。
- **官方来源**：[https://github.com/anthropics/skills](https://github.com/anthropics/skills)（文档：[https://github.com/anthropics/skills/tree/main/skills/pdf](https://github.com/anthropics/skills/tree/main/skills/pdf)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/anthropics/skills ~/anthropics-skills && ln -s ~/anthropics-skills/skills/pdf ~/.claude/skills/pdf`
- **如何使用**：处理 PDF 文档（读取、生成、提取、转换）时使用。

### Grilling（`grilling`）

- **简介**：基于「决策树」对用户的计划/决策/想法做一轮轮无情追问（每轮给出推荐答案），直到达成共同理解，用于压力测试思路、收敛设计决策。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/mattpocock/skills ~/mattpocock-skills && ln -s ~/mattpocock-skills/skills/productivity/grilling ~/.claude/skills/grilling`
- **如何使用**：想对某个计划/决策/想法做压力测试、逐层收敛「决策树」，或用户说「grill 我」时使用。
- **备注**：Matt Pocock 的 skills 合集（MIT）。grill-me / grill-with-docs 是其用户触发的变体。

### Leader（`leader`）

- **简介**：把一句话的想法拆成 AI agent 能独立跑完的目标任务书（≤4000 字符，可直接粘进 /goal），含实测数字、白名单地界、防作弊验收与断点续跑。
- **官方来源**：[https://github.com/KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)（文档：[https://github.com/KKKKhazix/khazix-skills/tree/main/leader](https://github.com/KKKKhazix/khazix-skills/tree/main/leader)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/KKKKhazix/khazix-skills ~/khazix-skills && ln -s ~/khazix-skills/leader ~/.claude/skills/leader`
- **如何使用**：要「给 agent 写目标/任务书/brief」「拆解目标」「让 agent 自己跑项目」「多 agent 并行」时使用。
- **备注**：卡兹克（KKKKhazix）开源合集（含 leader / neat-freak / hv-analysis 等）。
