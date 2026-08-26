#!/usr/bin/env python3
"""Reference evaluation harness for a quant-autoresearch project.

Contract (read-only during experiments; this is the evaluation contract):
    python backtest.py <run_dir> [--make-sample-data]

- Reads research.toml, loads data_file (CSV: date, close, volume).
- Calls strategy.generate_signals(df, params) -> Series of target positions in [-1, 1].
- Applies a one-bar execution delay (signal known at t earns the return of t+1).
- Applies transaction costs on position changes.
- Writes gross and net returns (returns.csv) so reports can re-evaluate costs offline.
- Compares the strategy against a buy-and-hold benchmark (alpha, beta, IR).
- Computes metrics on the OOS test segment (train metrics are auxiliary diagnostics).
- Writes <run_dir>/metrics.json (machine-readable contract) plus equity.csv and returns.csv.

--make-sample-data generates a deterministic synthetic price series first (smoke tests only).
"""

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def load_config(project):
    with open(project / "research.toml", "rb") as f:
        return tomllib.load(f)


def pin_data(project):
    data_dir = project / "data"
    files = sorted(p for p in data_dir.rglob("*") if p.is_file() and p.name != "VERSION")
    h = hashlib.sha256()
    for p in files:
        h.update(p.relative_to(data_dir).as_posix().encode())
        h.update(p.read_bytes())
    version = h.hexdigest()
    (data_dir / "VERSION").write_text(version + "\n")
    cfg = project / "research.toml"
    text = cfg.read_text()
    text = re.sub(r'(?m)^data_version\s*=\s*".*"$', f'data_version = "{version}"', text)
    cfg.write_text(text)
    return version


def make_sample_data(path, days=2600, seed=7):
    """Deterministic synthetic close series with weak momentum persistence."""
    rng = np.random.default_rng(seed)
    rets = rng.normal(0.0004, 0.01, days)
    for i in range(1, days):
        rets[i] += 0.08 * rets[i - 1]  # autocorrelation so momentum signals work
    close = 100.0 * np.exp(np.cumsum(rets))
    volume = rng.integers(1_000_000, 5_000_000, days)
    dates = pd.bdate_range("2014-01-01", periods=days)
    pd.DataFrame({"date": dates, "close": close, "volume": volume}).to_csv(path, index=False)


def compute_metrics(returns, positions, freq=252):
    n = len(returns)
    eq = (1.0 + returns).cumprod()
    total = float(eq.iloc[-1]) if n else 1.0
    ann_return = (total ** (freq / n) - 1.0) if n and total > 0 else -1.0
    vol = float(returns.std() * np.sqrt(freq)) if n > 1 else 0.0
    sharpe = float(returns.mean() / returns.std() * np.sqrt(freq)) if n > 1 and returns.std() > 0 else 0.0
    max_dd = float((eq / eq.cummax() - 1.0).min()) if n else 0.0
    t_stat = float(returns.mean() / returns.std() * np.sqrt(n)) if n > 1 and returns.std() > 0 else 0.0
    turnover = float(positions.diff().abs().mean()) if n else 0.0
    exposure = float(positions.abs().mean()) if n else 0.0
    return {
        "annual_return": ann_return,
        "annual_vol": vol,
        "sharpe": sharpe,
        "cumulative_return": total - 1.0,
        "max_drawdown": -max_dd,  # positive magnitude for max-limit constraints
        "t_stat": t_stat,
        "turnover": turnover,
        "exposure": exposure,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", help="output directory for this run")
    ap.add_argument("--make-sample-data", action="store_true", help="generate synthetic data first")
    args = ap.parse_args()

    project = Path.cwd()
    config = load_config(project)
    run_dir = Path(args.run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    if args.make_sample_data:
        data_path = project / config["project"]["data_file"]
        data_path.parent.mkdir(parents=True, exist_ok=True)
        make_sample_data(data_path)
        pin_data(project)
        config = load_config(project)

    data_path = project / config["project"]["data_file"]
    if not data_path.exists():
        sys.exit(f"data file not found: {data_path} (place data or run with --make-sample-data)")
    df = pd.read_csv(data_path, parse_dates=["date"]).set_index("date").sort_index()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")

    sys.path.insert(0, str(project))
    import strategy

    params = config.get("strategy_params", {})
    targets = strategy.generate_signals(df, params)
    positions = targets.shift(1).fillna(0.0).clip(-1.0, 1.0)
    rets = df["close"].pct_change().fillna(0.0)
    gross = positions * rets
    cost_bps = float(config["cost"]["bps"])
    cost = positions.diff().abs().fillna(positions.abs()) * cost_bps / 10000.0
    net = gross - cost

    split = int(len(net) * (1.0 - float(config["validation"]["test_fraction"])))
    test = net.iloc[split:]
    train = net.iloc[:split]
    test_pos = positions.iloc[split:]
    m_test = compute_metrics(test, test_pos)
    m_train = compute_metrics(train, positions.iloc[:split])
    m_full = compute_metrics(net, positions)

    # Benchmark: configured series (default: buy & hold of the underlying close).
    bench_cfg = config.get("benchmark", {})
    bench_name = str(bench_cfg.get("name", "buy_hold"))
    bench_code = str(bench_cfg.get("code", "") or "")
    if bench_code and bench_code in df.columns:
        bench_series = df[bench_code]
    else:
        bench_series = df["close"]
    bench_ret = bench_series.pct_change().fillna(0.0)
    test_bench = bench_ret.iloc[split:]
    m_bench = compute_metrics(test_bench, pd.Series(1.0, index=test_bench.index))
    cov_ = float(np.cov(test, test_bench)[0, 1]) if len(test) > 1 else 0.0
    var_ = float(np.var(test_bench)) if len(test_bench) > 1 else 0.0
    beta = cov_ / var_ if var_ > 0 else 0.0
    excess = test - test_bench
    alpha_ann = float((test.mean() - beta * test_bench.mean()) * 252)
    excess_ann = float((test.mean() - test_bench.mean()) * 252)
    ir = float(excess.mean() / excess.std() * np.sqrt(252)) if len(excess) > 1 and excess.std() > 0 else 0.0

    sig = targets.iloc[split:]
    fwd = rets.shift(-1).iloc[split:]
    ic = float(sig.rank().corr(fwd.rank())) if len(sig) > 3 else 0.0

    gross_ann = 0.0
    if len(test) > 0:
        total_gross = float((1.0 + gross.iloc[split:]).prod())
        gross_ann = total_gross ** (252 / len(test)) - 1.0 if total_gross > 0 else -1.0

    metric = config["project"]["metric"]
    metrics = {
        "schema_version": 1,
        "primary_metric": {"name": metric, "value": m_test[metric]},
        "constraints": {
            "max_drawdown": m_test["max_drawdown"],
            "turnover": m_test["turnover"],
            "exposure": m_test["exposure"],
        },
        "benchmark": {
            "name": bench_name,
            "annual_return": m_bench["annual_return"],
            "sharpe": m_bench["sharpe"],
            "max_drawdown": m_bench["max_drawdown"],
            "beta": beta,
            "alpha_ann": alpha_ann,
            "ir": ir,
            "excess_ann": excess_ann,
        },
        "t_stat": m_test["t_stat"],
        "auxiliary": {
            "train_primary": m_train[metric],
            "train_sharpe": m_train["sharpe"],
            "train_annual_return": m_train["annual_return"],
            "train_cumulative_return": m_train["cumulative_return"],
            "train_max_drawdown": m_train["max_drawdown"],
            "annual_return": m_test["annual_return"],
            "annual_vol": m_test["annual_vol"],
            "cumulative_return": m_test["cumulative_return"],
            "full_primary": m_full[metric],
            "full_sharpe": m_full["sharpe"],
            "full_annual_return": m_full["annual_return"],
            "full_cumulative_return": m_full["cumulative_return"],
            "full_max_drawdown": m_full["max_drawdown"],
            "ic": ic,
            "cost_bps": cost_bps,
            "gross_annual_return": gross_ann,
            "test_days": int(len(test)),
        },
        "data_version": config["project"]["data_version"],
        "periods": {
            "train": f"{df.index[0].date()} / {df.index[max(split - 1, 0)].date()}",
            "test": f"{df.index[split].date()} / {df.index[-1].date()}",
        },
        "runtime_seconds": round(time.time() - t0, 3),
    }
    (run_dir / "metrics.json").write_text(json.dumps(metrics, indent=2))
    pd.DataFrame({"gross": gross, "return": net, "position": positions}).to_csv(run_dir / "returns.csv")
    pd.DataFrame({"equity": (1.0 + net).cumprod()}).to_csv(run_dir / "equity.csv")
    print(json.dumps(metrics["primary_metric"], default=str))


if __name__ == "__main__":
    main()
