# 本仓库约定（给所有 agent）

这是一个个人 agent skills 收藏库，分两类资产：

1. **原创 skills**：源码 vendored 在 `skills/<分类>/<name>/`，可编辑、随仓库版本管理。
2. **第三方推荐 skills**：不 vendored 源码，只在 `recommended-skills.json`（机器可读清单）里记录官方来源与安装方式，需要时从上游安装。

本仓库不专属于 Claude Code，也适用于 Codex / Doubao / DeepSeek harness 等其他 agent。

## 你需要遵守的约定

- **第三方 skill 不要提交源码进仓库**，只更新 `recommended-skills.json`。
- **单一事实源**：`recommended-skills.json` 是权威数据；`recommended-skills.md` 由 `scripts/render_recommended.py` 生成，不要手改。
- **新增/修改第三方推荐**：先改 `recommended-skills.json`，再运行 `python3 scripts/render_recommended.py` 重新生成 `recommended-skills.md`。

## 当被要求「安装本仓库的 skills」「安装本仓库推荐的 skills」或初始化新环境时

本仓库有**两类 skills，安装时两类都要装、缺一不可**：

1. **原创 skills**：源码就在本仓库 `skills/<分类>/<name>/`。扫描 `skills/*/*/SKILL.md` 得到全集，把每个 `<name>/` 文件夹**完整复制**到当前 agent 自己的 skills 目录下，摊平为 `<name>/`（含 `SKILL.md`、`scripts/`、`references/` 等）。
2. **第三方推荐 skills**：清单是 `recommended-skills.json`（唯一事实源），源码不进仓库、按声明从上游安装。`install` 只含声明性字段，不提供现成命令：
   - `repo`：上游 git 仓库；
   - `path`：该 skill 在仓库中的子目录；
   - `requires`（可选）：运行时依赖的其他 skill 名。

   安装步骤：把上游 `repo` 取到临时目录（git clone 或下载 tarball 均可）→ 把 `path` 子目录完整复制为 skills 目录下的 `<name>/` → 删除临时目录；`requires` 列出的依赖必须一并装。

两类通用的规则：

- 复制语义：**每个 agent 由自己管理自己 skills 目录下的副本**（如 Claude Code 是 `~/.claude/skills/<name>/`）。
- **不要**在 `$HOME` 下长期 clone 一份共享代码再软链给各 agent 使用；重复安装/更新时直接整目录覆盖旧副本，保证幂等。
- 安装后检查 `<name>/SKILL.md` 的 `name` / `description` frontmatter 正确。
- **完整性自检**：原创全集 = `skills/*/*/SKILL.md` 匹配到的目录数；第三方全集 = `recommended-skills.json` 的 `skills` 数组长度。装完逐一核对，缺哪个补哪个。
- 若某第三方 skill 存在该 agent 专属的更原生安装渠道（如 Claude Code 插件市场），可在告知用户后改用之，但 `recommended-skills.json` 本身不记录这类命令。
