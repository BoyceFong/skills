# 本仓库约定（给所有 agent）

这是一个个人 agent skills 收藏库，分两类资产：

1. **原创 skills**：源码 vendored 在 `skills/<分类>/<name>/`，可编辑、随仓库版本管理。
2. **第三方推荐 skills**：不 vendored 源码，只在 `recommended-skills.json`（机器可读清单）里记录官方来源与安装方式，需要时从上游安装。

本仓库不专属于 Claude Code，也适用于 Codex / Doubao / DeepSeek harness 等其他 agent。

## 你需要遵守的约定

- **第三方 skill 不要提交源码进仓库**，只更新 `recommended-skills.json`。
- **单一事实源**：`recommended-skills.json` 是权威数据；`recommended-skills.md` 由 `scripts/render_recommended.py` 生成，不要手改。
- **新增/修改第三方推荐**：先改 `recommended-skills.json`，再运行 `python3 scripts/render_recommended.py` 重新生成 `recommended-skills.md`。

## 当被要求「安装本仓库推荐的 skills」或初始化新环境时

1. 读取 `recommended-skills.json` 的 `skills` 数组。
2. 逐条按 `install` 字段安装缺失的 skill：
   - `install.method = "plugin"`：这是 Claude Code 专属的插件装法（`claude plugin install ...`）。在其他 agent 环境下，改用 `source` 或 `install.repo` 从上游获取，按该 agent 的原生 skill 机制安装。
   - `install.method = "git"`：`git clone <repo>` 后，把 `install.path` 指向的 skill 文件夹复制/软链到该 agent 的 skills 目录。
   - `install.method = "copy"`：把 `SKILL.md`（含 `scripts/`、`references/` 等）复制/软链到该 agent 的 skills 目录。
3. 每个条目都提供 `source`（官方来源链接）。若某 agent 的 skill 机制与上述方式不同，一律以 `source` 为准，按该 agent 的原生方式安装。

## 原创 skills 的位置

原创 skill 在 `skills/<分类>/<name>/SKILL.md`（源码组织）。安装时摊平到目标 agent 的 skills 目录即可。
