# 推荐安装的第三方 skills

> 本文件由 `scripts/render_recommended.py` 从 `recommended-skills.json` 自动生成，勿手改。清单源数据见 [`recommended-skills.json`](./recommended-skills.json)。

## 工程

### Skill Creator（`skill-creator`）

- **简介**：Anthropic 官方技能创作工具，从零创建、修改、评测一个 skill，或优化 description 以提升触发准确率。
- **官方来源**：[https://github.com/anthropics/skills](https://github.com/anthropics/skills)（文档：[https://github.com/anthropics/skills/tree/main/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator)）
- **安装**：把 [https://github.com/anthropics/skills](https://github.com/anthropics/skills) 中的 `skills/skill-creator` 子目录整个复制到所用 agent 自己的 skills 目录下的 `skill-creator/`（复制语义，不用共享 clone + 软链）
- **如何使用**：当要创建新 skill、改进现有 skill，或跑评测 / 优化触发词时使用。
- **备注**：Anthropic 官方 skills 合集（另含 docx / pdf / pptx / xlsx 等）。同一技能也经官方插件市场分发（插件名同为 skill-creator），Claude Code 两种渠道效果等价。

### Grilling（`grilling`）

- **简介**：基于「决策树」对用户的计划/决策/想法做一轮轮无情追问（每轮给出推荐答案），直到达成共同理解，用于压力测试思路、收敛设计决策。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)）
- **安装**：把 [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills) 中的 `skills/productivity/grilling` 子目录整个复制到所用 agent 自己的 skills 目录下的 `grilling/`（复制语义，不用共享 clone + 软链）
- **如何使用**：想对某个计划/决策/想法做压力测试、逐层收敛「决策树」，或用户说「grill 我」时使用。
- **备注**：Matt Pocock 的 skills 合集（MIT）。grill-me / grill-with-docs 是其用户触发的变体。

### Grill Me（`grill-me`）

- **简介**：grilling 的用户手动触发版（disable-model-invocation），本体仅一行转发，执行与 grilling 相同的「设计树式无情追问」。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)）
- **安装**：把 [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills) 中的 `skills/productivity/grill-me` 子目录整个复制到所用 agent 自己的 skills 目录下的 `grill-me/`（复制语义，不用共享 clone + 软链），并一并安装依赖：`grilling`
- **如何使用**：只想用 /grill-me 显式手动触发、不希望模型自动触发时使用。
- **备注**：无独立逻辑，运行时依赖 grilling，依赖关系见 install.requires。

### Grill With Docs（`grill-with-docs`）

- **简介**：grilling 的文档增强版：追问收敛设计的同时叠加调用 domain-modeling，随手产出 ADR 架构决策记录与 CONTEXT.md 领域术语表。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)）
- **安装**：把 [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills) 中的 `skills/engineering/grill-with-docs` 子目录整个复制到所用 agent 自己的 skills 目录下的 `grill-with-docs/`（复制语义，不用共享 clone + 软链），并一并安装依赖：`grilling`、`domain-modeling`
- **如何使用**：想在压力测试设计决策的同时把结论沉淀为项目文档（ADR / glossary）时使用。
- **备注**：依赖 grilling 与 domain-modeling（后者含 ADR-FORMAT.md / CONTEXT-FORMAT.md 参考模板），依赖关系见 install.requires，需一并安装三者。

### Domain Modeling（`domain-modeling`）

- **简介**：构建并校准项目的领域模型：讨论代码库术语、编写或维护 CONTEXT.md 术语表、撰写 ADR 架构决策记录，附 ADR-FORMAT.md / CONTEXT-FORMAT.md 参考模板。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling)）
- **安装**：把 [https://github.com/mattpocock/skills](https://github.com/mattpocock/skills) 中的 `skills/engineering/domain-modeling` 子目录整个复制到所用 agent 自己的 skills 目录下的 `domain-modeling/`（复制语义，不用共享 clone + 软链）
- **如何使用**：需要沉淀领域术语表（CONTEXT.md）、记录架构决策（ADR），或聊到代码库术语命名时使用；可被模型自动触发。
- **备注**：自身无依赖，可独立使用。与 grill 系列的关系：grill-with-docs 依赖本 skill（其运行时同时调用 grilling + domain-modeling）；grilling / grill-me 不依赖它。

### Leader（`leader`）

- **简介**：把一句话的想法拆成 AI agent 能独立跑完的目标任务书（≤4000 字符，可直接粘进 /goal），含实测数字、白名单地界、防作弊验收与断点续跑。
- **官方来源**：[https://github.com/KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)（文档：[https://github.com/KKKKhazix/khazix-skills/tree/main/leader](https://github.com/KKKKhazix/khazix-skills/tree/main/leader)）
- **安装**：把 [https://github.com/KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 中的 `leader` 子目录整个复制到所用 agent 自己的 skills 目录下的 `leader/`（复制语义，不用共享 clone + 软链）
- **如何使用**：要「给 agent 写目标/任务书/brief」「拆解目标」「让 agent 自己跑项目」「多 agent 并行」时使用。
- **备注**：卡兹克（KKKKhazix）开源合集（含 leader / neat-freak / hv-analysis 等）。
