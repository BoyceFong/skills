# Hypothesis Playbook

The loop's fuel is hypotheses. One falsifiable hypothesis per run, with a mechanism, a knob, and an
expected effect. Read this when generating ideas or when the loop stalls.

## Hypothesis template

```
H-<n>: <claim>
Economic rationale: <why it should work>
Test: modify <knob> in strategy.py (expected effect: <direction, rough magnitude>)
Falsified if: <observable condition>    # e.g. OOS Sharpe does not improve by >= threshold
```

Record the ID and rationale in the run description so the ledger reads as a research narrative.

## Sources of hypotheses (roughly in order of expected hit rate)

1. **Diagnose-driven** (best): every failure and every weak keep suggests the next test. A drawdown
   cluster in high-volatility regimes suggests a vol filter. High turnover with low net gain
   suggests cost-aware rebalancing. Re-read `diagnostics.md` first.
2. **Engineering / cost reduction**: reduce turnover, execution delay, or parameter sensitivity.
   These often have real effects at lower overfitting risk than new alpha.
3. **Established factor families** (with mechanism, not just names):
   - Time-series: momentum, reversal, moving-average/trend filters, vol targeting, carry.
   - Cross-sectional: value, quality, low-volatility, liquidity, skewness, funding.
   - Microstructure: opening/closing behavior, volume/VWAP placement, bid-ask pressure.
   - Regime: trend/vol/rate regimes as filters or gates.
   - Multi-factor: combine low-correlation signals; weight by IC or risk parity; orthogonalize.
4. **Literature**: when stuck, read the papers referenced in the code or search for the asset class
   and factor in question. Re-implement a published signal faithfully, then let the loop adapt it.

## Discipline rules

- **One change per run.** Two simultaneous edits make it impossible to attribute the result.
- **Mechanism over pattern.** A correlation without a story is usually noise; if you cannot say why
  it should persist, treat it as a candidate for the discard pile.
- **Cheap first.** Prefer hypotheses that take a few lines and low risk: parameter changes, small
  gates, cost-aware tweaks. Save structural rewrites for when cheap ideas are exhausted.
- **Prioritize robustness over peak.** A modest, stable improvement beats a large one that only
  works in one split.
- **Combine near-misses.** Two failed hypotheses that failed for the same reason often point to one
  better hypothesis. Use the failure taxonomy in `diagnostics.md` to cluster them.
- **No data dredging.** Do not try dozens of variants and keep the winners without adjusting the
  bar. Every extra trial raises the false-positive rate; re-read `protocol.md` section 5.
- **ML with discipline.** If fitting models, use nested validation so the loop's OOS is never seen
  during fitting, keep feature counts small relative to observations, and treat any ML edge with
  extra skepticism until the robustness battery passes.

## When the loop stalls

- Verify you are testing hypotheses, not tuning noise (acceptance rate near zero for many runs).
- Re-read past near-misses and failures; cluster their diagnoses.
- Change category: if signal ideas are exhausted, switch to cost/execution or risk-management
  hypotheses.
- Re-read the literature for the asset class. Karpathy's agents re-read code and papers when out of
  ideas; do the same.
- Consider whether the objective itself is unreachable with the current data/constraints, and say so
  in the report rather than burning runs.

## Anti-patterns

- "Hope" hypotheses with no mechanism and no falsification condition.
- Tuning on the frozen OOS segment (this is the cardinal sin — it spends the research budget).
- Chasing the leaderboard: over-optimizing one metric while constraints silently degrade.
- Adding complexity for tiny gains ("ugly 20-line hack for 0.001" — the protocol says discard).

## 模式与假设策略

- Explorer（发散）：优先尝试新因子算子、新结构、另类逻辑；失败是研究样本，允许大胆试错，
  接受率低是常态，重点是样本积累与机制线索。
- Refiner（收敛）：只做参数邻域、过滤条件、风控、特征精简类假设，每次只动一个旋钮；增益
  微小且代码变复杂的改动会被决策规则直接拒绝，不值得跑。
