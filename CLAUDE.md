# 本仓库约定（给 Claude Code）

这是一个个人 agent skills 收藏库，分两类资产：

1. **原创 skills**：源码 vendored 在 `skills/<分类>/<name>/`，可编辑、随仓库版本管理。
2. **第三方推荐 skills**：不 vendored 源码，只在 `recommended-skills.json`（机器可读清单）里记录官方来源与安装方式，需要时从上游安装。

> 跨 agent（Codex / Doubao / DeepSeek 等）的通用约定见 `AGENTS.md`。

## 你需要遵守的约定

- **第三方 skill 不要提交源码进仓库**，只更新 `recommended-skills.json`。
- **单一事实源**：`recommended-skills.json` 是权威数据；`recommended-skills.md` 由 `scripts/render_recommended.py` 生成，不要手改。
- **新增/修改第三方推荐**：先改 `recommended-skills.json`，再运行 `python3 scripts/render_recommended.py` 重新生成 `recommended-skills.md`。

## 当被要求「安装本仓库推荐的 skills」或初始化新环境时

1. 读取 `recommended-skills.json` 的 `skills` 数组。
2. 逐条按 `install` 字段安装缺失的 skill（`install.method` 的取值与对应安装方式）：
   - `plugin`：`claude plugin marketplace add <marketplace>`（若未添加）→ `claude plugin install <plugin>[@<marketplace>]`。
   - `git`：`git clone <repo>` 后，把 `install.path` 指向的 skill 文件夹软链/复制到 `~/.claude/skills/<name>/`。
   - `copy`：把 `SKILL.md`（含 `scripts/`、`references/` 等）复制/软链到 `~/.claude/skills/<name>/`。
3. 安装后可用 `/reload-skills` 刷新，或在 `~/.claude/skills/<name>/SKILL.md` 确认 `name` / `description` frontmatter 正确。

## 原创 skills 的位置

原创 skill 在 `skills/<分类>/<name>/SKILL.md`（源码组织）。安装时需摊平：把 `skills/<分类>/<name>` 软链/复制到 `~/.claude/skills/<name>`。
