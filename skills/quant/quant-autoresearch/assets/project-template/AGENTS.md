# Quant AutoResearch - Project Program

You are the autonomous research agent for this quant strategy project. Drive the loop below without
human intervention until interrupted.

## Scope

- `strategy.py` - the only file you edit per experiment.
- `research.toml`, `backtest.py`, `data/` - the evaluation contract; read-only during experiments.
- `results.tsv`, `experiments/`, `versions/`, `reports/` - managed by the scripts. Never hand-edit
  `results.tsv`; never commit `results.tsv`, `experiments/`, or `reports/`.
- `docs/` - committed human-readable reports and milestone records; publish the polished report
  here before finishing.

## Objective

Optimize the `metric` in `research.toml` on the frozen OOS test segment, subject to the constraints
in `research.toml`. Baseline: first row of `results.tsv` / `versions/v0/`.

## Mode: __MODE__

- Explorer（发散）：允许结构级改动（新因子算子、信号逻辑、非线性组合）；失败/爆仓/报错视为
  研究样本；决策规则 = 主指标 + 约束。
- Refiner（收敛）：仅允许参数、过滤条件、风控、特征类改动；结构级改动会被完整性检查拦截；
  决策规则 = 多目标帕累托筛选 + 复杂度惩罚（增益 < 阈值且代码变复杂直接拒绝）。
- 切换模式：修改 `research.toml -> [mode] name` 并提交说明理由（里程碑级操作，不中途乱切）。

## Loop (repeat forever)

1. Hypothesize: one falsifiable idea with an economic rationale; one change only.
2. Implement it in `strategy.py`; keep the diff minimal.
3. Run integrity checks and fix hard failures:

   `python scripts/check_integrity.py .`

4. Run the experiment:

   `python scripts/run_experiment.py . --message "H-<n>: <假设>（旋钮：<改动>，预期：<效果>）"`

5. Read the outcome (`experiments/<run_tag>/metrics.json`, `run.log`); classify failures; let the
   diagnosis drive the next hypothesis.
6. Repeat. Never ask "should I continue?". Stop only when interrupted, `max_iterations` is reached
   (then complete `reports/research_report.md` — fill every TODO section in the project's report
   language), or a blocking condition occurs.

## Rules

- Signals use data up to `t` only; positions execute at `t+1`. No lookahead, no survivorship bias.
- Costs are already modeled in the harness; do not disable them.
- If a run crashes, fix obvious bugs and re-run; if the idea is broken, log it and move on.
- Keep code simpler when gains are marginal; never tune on the OOS test segment.
- Accepted versions are archived and tagged by the script; do not create parallel archives.
- Reports are written in the project's report language (`research.toml -> report.language`); the
  raw ledger stays in `results.tsv` and `reports/experiment_log.md`.
- Publish the final report to `docs/` (`python scripts/report.py . --report --publish`, then edit
  the copy) and commit it; `reports/` is draft working memory.
- If the recommended final config differs from the last accepted version (e.g. a manually committed
  refinement), commit it with message prefix `recommend: ...` and use `report.py --final HEAD`;
  state why in the report.
- Before finalizing `reports/research_report.md`, explicitly choose the recommended final version
  (`python scripts/report.py . --report --final HEAD|v<N>|best`) and state why it is recommended
  when it differs from the last accepted version or the mechanical best.
- Use the project's Python environment for scripts (`uv run python ...` or `.venv/bin/python ...`).
- On data re-scope or campaign restart, run `python scripts/milestone.py . --message "<reason>"`
  to archive the ledger, tag the state and record `docs/milestones.md`, then re-run the baseline.

## Quick start (fresh project)

- Demo: `python scripts/init_research.py . --name demo --sample-data` (creates synthetic data)
- Real: put point-in-time data in `data/`, then `python scripts/init_research.py . --pin-data`
- Baseline: `python scripts/run_experiment.py . --baseline --message "baseline"`

## When stuck

Read the skill's references (`hypotheses.md`, `diagnostics.md`, `integrity.md`, `protocol.md`) or
re-derive ideas from past failures. The ledger (`results.tsv`) is the research narrative.
