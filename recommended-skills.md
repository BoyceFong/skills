# 推荐安装的第三方 skills

> 本文件由 `scripts/render_recommended.py` 从 `recommended-skills.json` 自动生成，勿手改。清单源数据见 [`recommended-skills.json`](./recommended-skills.json)。

## 工程

### Skill Creator（`skill-creator`）

- **简介**：Anthropic 官方技能创作工具，从零创建、修改、评测一个 skill，或优化 description 以提升触发准确率。
- **官方来源**：[https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/skill-creator)
- **安装**：`claude plugin install skill-creator@claude-plugins-official`
- **如何使用**：当要创建新 skill、改进现有 skill，或跑评测 / 优化触发词时使用。

### Grilling（`grilling`）

- **简介**：基于「决策树」对用户的计划/决策/想法做一轮轮无情追问（每轮给出推荐答案），直到达成共同理解，用于压力测试思路、收敛设计决策。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/mattpocock/skills ~/mattpocock-skills && ln -s ~/mattpocock-skills/skills/productivity/grilling ~/.claude/skills/grilling`
- **如何使用**：想对某个计划/决策/想法做压力测试、逐层收敛「决策树」，或用户说「grill 我」时使用。
- **备注**：Matt Pocock 的 skills 合集（MIT）。grill-me / grill-with-docs 是其用户触发的变体。

### Grill Me（`grill-me`）

- **简介**：grilling 的用户手动触发版（disable-model-invocation），本体仅一行转发，执行与 grilling 相同的「设计树式无情追问」。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/mattpocock/skills ~/mattpocock-skills && ln -s ~/mattpocock-skills/skills/productivity/grilling ~/.claude/skills/grilling && ln -s ~/mattpocock-skills/skills/productivity/grill-me ~/.claude/skills/grill-me`
- **如何使用**：只想用 /grill-me 显式手动触发、不希望模型自动触发时使用。
- **备注**：无独立逻辑，运行时依赖 grilling，安装命令已一并软链 grilling。

### Grill With Docs（`grill-with-docs`）

- **简介**：grilling 的文档增强版：追问收敛设计的同时叠加调用 domain-modeling，随手产出 ADR 架构决策记录与 CONTEXT.md 领域术语表。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs](https://github.com/mattpocock/skills/tree/main/skills/engineering/grill-with-docs)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/mattpocock/skills ~/mattpocock-skills && ln -s ~/mattpocock-skills/skills/productivity/grilling ~/.claude/skills/grilling && ln -s ~/mattpocock-skills/skills/engineering/domain-modeling ~/.claude/skills/domain-modeling && ln -s ~/mattpocock-skills/skills/engineering/grill-with-docs ~/.claude/skills/grill-with-docs`
- **如何使用**：想在压力测试设计决策的同时把结论沉淀为项目文档（ADR / glossary）时使用。
- **备注**：依赖 grilling 与 domain-modeling（后者含 ADR-FORMAT.md / CONTEXT-FORMAT.md 参考模板），安装命令已一并软链三者。

### Domain Modeling（`domain-modeling`）

- **简介**：构建并校准项目的领域模型：讨论代码库术语、编写或维护 CONTEXT.md 术语表、撰写 ADR 架构决策记录，附 ADR-FORMAT.md / CONTEXT-FORMAT.md 参考模板。
- **官方来源**：[https://github.com/mattpocock/skills](https://github.com/mattpocock/skills)（文档：[https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling](https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/mattpocock/skills ~/mattpocock-skills && ln -s ~/mattpocock-skills/skills/engineering/domain-modeling ~/.claude/skills/domain-modeling`
- **如何使用**：需要沉淀领域术语表（CONTEXT.md）、记录架构决策（ADR），或聊到代码库术语命名时使用；可被模型自动触发。
- **备注**：自身无依赖，可独立使用。与 grill 系列的关系：grill-with-docs 依赖本 skill（其运行时同时调用 grilling + domain-modeling）；grilling / grill-me 不依赖它。

### Leader（`leader`）

- **简介**：把一句话的想法拆成 AI agent 能独立跑完的目标任务书（≤4000 字符，可直接粘进 /goal），含实测数字、白名单地界、防作弊验收与断点续跑。
- **官方来源**：[https://github.com/KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills)（文档：[https://github.com/KKKKhazix/khazix-skills/tree/main/leader](https://github.com/KKKKhazix/khazix-skills/tree/main/leader)）
- **安装**：`mkdir -p ~/.claude/skills && git clone --depth 1 https://github.com/KKKKhazix/khazix-skills ~/khazix-skills && ln -s ~/khazix-skills/leader ~/.claude/skills/leader`
- **如何使用**：要「给 agent 写目标/任务书/brief」「拆解目标」「让 agent 自己跑项目」「多 agent 并行」时使用。
- **备注**：卡兹克（KKKKhazix）开源合集（含 leader / neat-freak / hv-analysis 等）。
