# Backtest Integrity

The loop is only as good as the backtest. A leakage bug turns every decision into noise, so
integrity is a hard gate, not a nice-to-have. Use this checklist when implementing signal code and
when reviewing any diff.

## 1. Leakage taxonomy

- **Lookahead**: using information not available at bar `t` when deciding the position at `t`.
  Examples: `shift(-1)` / negative `pct_change`, forward fills, full-sample statistics computed
  inside the signal, using the close of `t` to trade at the close of `t`, future earnings, future
  index membership.
- **Execution timing**: a signal known at `t` must earn the return of `t+1` (or later). The
  reference harness applies `targets.shift(1)` automatically; if you replace the harness, preserve
  this. Trading at `t` with `t`'s close is lookahead.
- **Survivorship bias**: a universe built from today's constituents ignores delisted names.
  Universe membership must come from a point-in-time snapshot.
- **Data alignment**: timestamps, timezones, and bar semantics must match. Closing-price series
  must be aligned to their own timestamps; corporate actions (splits, dividends) must be adjusted
  consistently; `dropna` can silently misalign rows.
- **In-sample/out-of-sample**: parameters or models must be fit only on train data. Standardizing
  with full-sample statistics, or training an ML model on the whole history, leaks test information
  into the signal.
- **Costs**: commission, slippage, borrow cost (for shorts), and market impact must be modeled.
  Zero-cost backtests overstate net returns and reward turnover. Document the cost assumptions.
- **Capacity**: positions must respect liquidity and notional limits; check daily turnover and
  exposure. A result that only works with unbounded size is not a result.

## 2. Code-review checklist (apply to every diff)

1. Signal function uses only rows up to the current index: no `shift(-k)`, `pct_change(-k)`,
   `diff(-k)`, `bfill()`, or future-index access.
2. Rolling/expanding windows are closed at the current bar (`rolling(k)` uses `t-k+1..t` — verify
   with small examples when in doubt).
3. No full-sample statistics inside the signal path (`mean()`, `std()`, `quantile()`, `describe()`
   on the whole series).
4. Any `resample`/`reindex` preserves alignment; test with a tiny frame before running.
5. Universe membership is point-in-time, not a current snapshot.
6. If the strategy fits parameters (including ML models), fitting uses train data only; validation
   is nested so the loop's OOS is never touched during fitting.
7. Position changes execute next bar in the harness.
8. Costs are applied to turnover, including the first day's position.
9. `data/VERSION` matches `research.toml -> data_version` and the data was not modified during the
   run.
10. The diff touches only `allowed_files`; harness and data are untouched.

## 3. Automated checks

`check_integrity.py` statically scans the allowed files for the most common patterns
(negative shifts, forward fills, full-sample stat calls, resampling, nondeterminism) and verifies
scope + data version. It returns hard failures (block the run) and warnings (review before
running). Static checks are heuristics — they cannot prove correctness. When in doubt, test the
signal function on a tiny hand-verified frame.

## 4. Data versioning

- `data/VERSION` is a content hash of everything under `data/` (excluding itself), computed by
  `init_research.py --pin-data`.
- Any change to data — new rows, a different adjust factor, a corrected tick — changes the hash and
  invalidates all prior results. Re-pin only at a declared milestone, re-run the baseline, and
  re-archive.
- Keep the raw data provenance somewhere immutable (original file hash, vendor, download date) in a
  `data/SOURCES` note if it exists; the pin alone proves nothing changed since pinning.

## 5. When you find a leak

1. Stop the loop immediately (finish the current run, then pause).
2. Fix the leak in the code, not in the data.
3. Re-pin data if the data itself was wrong.
4. Re-run the baseline and mark earlier results as invalid in the ledger (append a `discard`
   row with description `invalidated: <reason>` — the ledger is append-only).
5. Resume only after the integrity gate passes.
