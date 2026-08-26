# Experiment Protocol

This is the constitution of a quant-autoresearch project: how experiments are defined, evaluated,
kept, reverted, and archived. Read it at setup and whenever the decision rule is in doubt.

## 1. Fixed evaluation contract

Comparability is the foundation of the loop (Karpathy's core design: one metric, fixed budget, one
mutable file). In a quant project the contract is:

- **One primary metric.** Stored as `metric` in `research.toml` (e.g. `sharpe`, `sortino`, `ic`).
  All keep/revert decisions use it. Auxiliary metrics are diagnostics only.
- **One mutable file.** `strategy.py` (configurable via `allowed_files`). Everything else that
  affects evaluation is read-only during a run: `data/`, `backtest.py`, `research.toml`.
- **Fixed budget.** `budget_seconds` in `research.toml` bounds each backtest so runs are comparable
  regardless of what changed. The harness must finish within `timeout_seconds` (default 2x budget);
  the runner kills it and logs `crash` otherwise.
- **Pinned data.** `data/VERSION` must equal `research.toml -> data_version`. Changing data
  invalidates every prior result; re-pin only at declared milestones.

## 2. Validation design

The primary metric is always computed on an out-of-sample (OOS) segment, never on data used to
inspire or fit the strategy:

- Split the history into train and test (`test_fraction` in `research.toml`). The harness reports
  test metrics as the decision inputs; train metrics are auxiliary diagnostics.
- The test segment is frozen for the whole research campaign. Never tune on it, never re-split to
  make a result look better, and never compare variants that were selected by peeking at test
  results — that burns the research budget (see section 5).
- For factor or cross-sectional research, prefer walk-forward evaluation: re-fit parameters on a
  rolling/expanding window and evaluate on the next unseen block, chaining blocks. The primary
  metric is then the pooled OOS result.
- A change that only helps one split or one regime is usually noise; verify with the diagnostics in
  `diagnostics.md` before trusting it.

## 3. Decision rule

The runner (`run_experiment.py`) computes, mechanically:

```
base     = primary metric of the last accepted row (baseline or keep)
required = max(min_improvement * abs(base), min_improvement_abs)
improved = (new - base) >= required          if direction == "higher"
           (new - base) <= -required         if direction == "lower"

accept iff improved
          AND every configured constraint passes
          AND (min_t_stat == 0 OR t_stat >= min_t_stat)
```

Constraints are declared as `[decision.constraints.<name>] limit + kind (max|min)` in
`research.toml`; the harness reports each value in `metrics.json -> constraints`. Common ones:
max drawdown, daily turnover, gross exposure, position count, capacity.

Defaults are deliberately conservative: 5% relative improvement (`min_improvement = 0.05`) plus
constraints. Raise the bar as experiments accumulate — with N runs you expect false positives, so
for factor research prefer a significance gate (`min_t_stat`), a deflated-Sharpe adjustment, or a
stricter `min_improvement` once N exceeds ~50.

**Simplicity is part of the rule.** For a marginal gain, keep the simpler code. For an equal result,
always keep the simpler code. Record the judgment in the run description.

## 4. Git discipline

- Work on an `autoresearch/<date>` branch created at setup. Each experiment is one commit.
- Keep: the commit stays, `versions/v<N>/` is snapshotted (strategy, config, metrics, description),
  and the commit is tagged `v<N>`.
- Discard: the runner does `git reset --hard` to the pre-experiment commit. Rejected code never
  survives in history except in the ledger.
- Crash: the commit is left in place so you can fix forward; the ledger records `crash`. Do not
  re-run the same code silently — each run gets its own ledger row.
- Never commit `results.tsv`, `experiments/`, or `reports/`; they are the working memory, not the
  artifact.

## 5. Multiple testing and overfitting

The loop is a search; searching generates false positives. Guardrails:

- Never tune on OOS. OOS is spent the first time you look at it and adjust.
- Prefer hypotheses with an economic mechanism over pure curve-fitting. A result without a reason
  is a candidate for the discard pile.
- Apply the robustness battery in `diagnostics.md` before trusting a structural change.
- Track the acceptance rate. Healthy is roughly 20-40%. Zero for many runs means the hypotheses are
  weak or the bar is unreachable; 100% means the bar is too lenient or something is leaking.

## 6. Crash and timeout policy

- Timeout or nonzero exit: log `crash`, read `run.log`, fix obvious bugs (typo, missing import,
  wrong column name), re-run. If the idea itself is broken, abandon it and move on.
- Three consecutive crashes on the same idea: abandon the idea.
- Invalid `metrics.json` (schema, missing primary value, data version mismatch): treat as a harness
  defect, log `crash`, and report it. Fixing `backtest.py` is legitimate maintenance, but it
  invalidates comparability with prior runs — re-run the baseline and re-archive if needed.

## 7. Autonomy policy

- The loop never stops on its own. Do not ask "should I continue?". Stop only when: the human
  interrupts; `autonomy.max_iterations` (if > 0) is reached — then write the final report; or a
  blocking condition occurs (missing data, permission, dependency install, disk full), which you
  surface with the exact blocker.
- The final report (`reports/research_report.md`) is a human-readable narrative, not the ledger.
  Write it in the project's report language (`research.toml -> report.language`), fill every TODO
  section, and keep the raw flow in `results.tsv` / `reports/experiment_log.md`.
- Designate the recommended final version explicitly when writing the report (`report.py --final`,
  default `HEAD`). The mechanical best and the last accepted version are data; the recommendation is
  a judgment — when they differ, state the reason (robustness, simplicity, capacity, cost).
- `autonomy.checkpoint_every` (if > 0) pauses after that many runs with a one-line summary, then
  resumes without asking for confirmation.
- The ledger (`results.tsv`) is the source of truth for what happened. Keep descriptions
  tab-free and structured as `假设（旋钮：<改动>，预期：<效果>）` so the ledger reads as a
  research narrative.
- On data re-scope or campaign restart, use `milestone.py` (archive ledger, tag
  `milestone/<timestamp>`, record `docs/milestones.md`) instead of hand-editing or clearing the
  ledger; then re-run the baseline.
- A final recommendation that differs from the last accepted version (e.g. a manually committed
  refinement) is a judgment call: commit it with message prefix `recommend: ...`, designate it via
  `report.py --final HEAD`, and explain why in the report.

## 8. 双模式（Explorer / Refiner）

- `research.toml -> [mode] name` 定义当前模式（默认 explorer）。切换是里程碑级操作：改配置并
  提交说明理由，不中途乱切；报告头部标注当前模式。
- Explorer：允许结构级改动（新因子算子、信号逻辑、非线性组合）；决策 = 主指标 + 约束；崩溃/
  失败作为研究样本，有研究价值的失败在描述中加 `[sample]` 前缀，供后续借鉴。
- Refiner：仅允许参数、过滤、风控、特征类改动；`check_integrity.py` 对结构指纹（imports、
  def/签名、参数键集）做硬校验，结构改动即失败；决策 = 约束门 + 帕累托支配（Sharpe / Calmar /
  最大回撤 / 训练一致性，容差 `[mode.refiner].eps`）+ 复杂度惩罚（增益 < 阈值且 diff 行数 >
  `[mode.refiner].complexity_lines` 直接拒绝）。
- 两种模式共用账本、版本归档与报告基础设施；账本里不混口径（同一次 campaign 内模式固定）。

## 9. 因子专项与决策门（可选）

- 因子类项目：harness 可在 `metrics.json` 输出可选 `factor` 块（对象），`report.py` 检测到后
  自动渲染「因子专项分析」章节（指标表、Rank IC 衰减表、分层表现表，图表在 matplotlib 可用时
  生成）。块结构：

  ```json
  "factor": {
    "name": "composite_score",
    "ic": 0.028, "rank_ic": 0.030, "icir": 1.2,
    "long_short_annual": 0.05, "long_short_sharpe": 0.6,
    "decay": [{"horizon": 1, "rank_ic": 0.030}, {"horizon": 2, "rank_ic": 0.021}],
    "quantiles": [{"quantile": "Q1", "annual_return": 0.12, "sharpe": 0.8}]
  }
  ```

  键缺失时对应子表自动隐藏；模板单资产 harness 不输出该块，章节不出现。
- 报告自动生成「Gate 对照表」：主指标相对基线改善、全部配置约束、OOS/IS > 0、训练/OOS 同向、
  DSR ≥ 0.95，逐项 pass/fail；结论建议（continue / kill / promote）由 agent 撰写并给出理由
  与所需证据，使报告以决策语言收尾。
