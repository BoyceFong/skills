# llm-wiki-ops

`llm-wiki-ops` 是一个面向飞书知识库的 Agent Skill，用于把原始资料和文章持续整理成可查询、可追溯、互相双链的 LLM Wiki。

## 功能

- 初始化新的 LLM Wiki，或绑定已有飞书知识空间
- 将原始资料整理成资料卡，并提取实体、概念和方法论词条
- 将文章区分为成稿和草稿入库
- 基于索引查询知识库，并用来源文档支撑关键结论
- 检查孤儿页、双链、来源标注、索引一致性、矛盾和过期内容
- 维护 A-Z 索引与追加式更新日志

## 前置条件

- Agent 支持 `SKILL.md`，或者兼容开放的 Agent Skills 规范
- 已安装并授权 `lark-cli`，或具有等价的飞书知识库、云文档和云空间工具
- 飞书账号拥有目标知识空间和文档的相应读写权限
- 处理图片型 PDF 时，需要 PDF 页面渲染和视觉读取能力

## 安装

本技能 vendored 在本仓库 `skills/engineering/llm-wiki-ops/`。安装时把该目录**整个复制**到 Agent 自己的 skills 目录下、摊平为 `llm-wiki-ops/`（复制语义，不要共享 clone + 软链）：

```bash
git clone https://github.com/BoyceFong/skills.git
cd skills
cp -R skills/engineering/llm-wiki-ops ~/.claude/skills/llm-wiki-ops   # Claude Code
```

在 Codex 中，个人 Skill 可以安装到 `$HOME/.agents/skills`：

```bash
cp -R skills/engineering/llm-wiki-ops "$HOME/.agents/skills/llm-wiki-ops"
```

安装完成后，如果 Agent 没有立即发现 Skill，请重新加载 Skills 列表或重启 Agent。

## 使用

首次使用时显式调用：

```text
$llm-wiki-ops 帮我初始化或绑定一个 LLM Wiki。
```

绑定完成后可以直接入库、查询或体检：

```text
$llm-wiki-ops 把这份资料入库，并建立相关词条之间的双链。
```

```text
$llm-wiki-ops 查询知识库中关于 RAG 评测的资料，关键结论标注来源。
```

```text
$llm-wiki-ops 对知识库做一次完整体检。
```

## 绑定配置与隐私

`config/wiki-binding.json` 是首次初始化或绑定后生成的本地运行时状态，包含知识空间 ID、节点 token、文档 ID 和知识库地址。

- 真实的 `wiki-binding.json` 已被 `.gitignore` 排除，不应提交到公开仓库。
- 仓库只提供脱敏的 [`wiki-binding.example.json`](config/wiki-binding.example.json) 说明配置结构。
- 不要把示例文件直接改名后当成有效绑定；应让 Skill 通过初始化流程生成并验证真实配置。
- 如果真实绑定文件曾经进入 Git 历史，仅在新提交中删除并不能清除历史记录。

## 目录结构

```text
llm-wiki-ops/
├── SKILL.md
├── README.md
├── LICENSE
├── .gitignore
├── config/
│   └── wiki-binding.example.json
└── references/
    ├── entry-template.md
    ├── ingest.md
    ├── init.md
    ├── lint.md
    └── query.md
```

## 限制

- 当前每份安装只绑定一个 LLM Wiki。
- 多个 Agent 不应同时修改同一份索引和双链，避免重复词条或覆盖更新。
- 实时资讯查询依赖额外的资讯数据源；本 Skill 默认只依据用户提供和已入库的资料。
- 定时体检需要宿主 Agent 或外部调度器另行配置。

## 来源与修改

本技能基于刘聪NLP（[liucongg](https://github.com/liucongg)）开源的 [llm-wiki-ops](https://github.com/liucongg/liucong-skills/tree/main/skills/llm-wiki-ops)（Apache-2.0）vendored 进本仓库，随仓库版本维护，后续修改直接在本目录进行。

Wiki 框架方法论来自 Andrej Karpathy 的 [LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)：让 LLM 把原始资料持续编译成互相链接的持久化 wiki，而非传统 RAG 检索。

- 2026-09-01：维护手册文件名约定由 `AGENT.md` 改为业界通用的 `AGENTS.md`（同步修改 SKILL.md、references/init.md、config/ 示例与说明）。

## License

Apache License 2.0（继承自上游）。详见本目录的 [`LICENSE`](LICENSE)。
