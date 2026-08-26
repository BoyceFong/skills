# Diagnosis Playbook

Every run produces evidence. The diagnosis converts that evidence into the next hypothesis.
Diagnose after every keep and every failure; the loop compounds only if you do.

## Diagnostic workflow

For each run, inspect `experiments/<run_tag>/metrics.json` and `run.log`, plus the diagnostic
artifacts the harness writes (returns/equity series), and work through:

1. **Result vs decision inputs.** Did it pass/fail the mechanical rule, and by how much? Was it
   close (near-miss) or far off?
2. **Attribution.** Decompose net performance into signal contribution, market exposure, and cost
   drag. Compare gross vs net; a big gap means costs dominate (fix: lower turnover or costs).
3. **Drawdown structure.** Where are the drawdowns clustered? Associate them with regimes
   (volatility, trend, rates) — this suggests regime-gating hypotheses.
4. **Sub-period stability.** Break test returns into yearly/quarterly blocks. Consistent positive
   blocks = signal; one lucky block = noise. A strategy that loses in 40%+ of blocks rarely
   survives live conditions.
5. **Signal diagnostics.** IC / rank-IC, hit rate, signal autocorrelation, decay horizon. If IC is
   positive only at horizon k, the holding period should match k.
6. **Parameter sensitivity.** Perturb each key knob by ±10-20% (run as additional experiments, not
   silent tuning). If the result flips sign or collapses, it is noise or overfit.
7. **Turnover and exposure.** Is the edge dependent on frequent trading or high leverage? Each
   implies capacity and cost risk.

## Failure taxonomy (and the next hypothesis)

| Diagnosis | Evidence | Next step |
|---|---|---|
| Data bug / leakage | implausible returns, integrity check hit | fix code or data, re-run, invalidate affected rows |
| Noise / overfit | good only in one split, parameter-sensitive | simplify, require larger effect, raise the bar, fewer knobs |
| Cost drag | gross edge healthy, net poor, high turnover | reduce turnover, lower frequency, execution-aware sizing |
| Alpha decay | IC strong at short horizon only, weak at holding | shorten holding, re-express the signal, regime filter |
| Regime dependence | losses cluster in one regime | add explicit regime gate or exposure control |
| Capacity / liquidity | edge concentrated in illiquid names | shrink universe, cap positions, measure slippage |
| Correlation / concentration | few names or one factor drive returns | diversify, orthogonalize, risk parity |

## Health signals of the loop itself

Healthy:

- Acceptance rate ~20-40%; early improvements are the largest, then diminishing.
- Ledger shows a narrative: each keep has a mechanism; discards are classified, not random.
- Metric trend improves early and plateaus — plateau means you have found the strategy's level
  under the current constraints, not that the loop is broken.

Unhealthy:

- Acceptance rate 100% — the bar is too lenient or something leaks.
- Acceptance rate 0% for a long stretch — hypotheses are weak or the objective is unreachable with
  this data/constraint set.
- Metric jumps up then reverts — likely leakage or overfit; run integrity checks.
- Complexity grows without metric growth — enforce the simplicity rule.

## What to record

In the run description or a `reports/` note, record: the hypothesis, the diagnosis, and the next
idea it suggests. The report (`report.py --report`) aggregates these into the research narrative;
the narrative is what makes the archive valuable later.

## 模式相关诊断

- Explorer：失败进入分类法并可用 `[sample]` 前缀标记，作为后续假设素材；重点关注机制线索与
  意外现象，而非单项指标。
- Refiner：重点看帕累托各项的边际变化——任一准则退化（超出容差）即被拒绝；复杂度惩罚意味着
  “小幅提升 + 大量新代码”应直接放弃，诊断应聚焦参数邻域的稳健性（±10%~20% 扰动）。
