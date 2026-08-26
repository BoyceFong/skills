#!/usr/bin/env python3
"""Human-readable research report and separate experiment ledger.

Usage:
  report.py <project_dir> [--report] [--top N] [--final <ref>] [--publish]

--final selects the recommended final strategy whose parameters/rules and charts the report
shows. Supported refs:
  HEAD     current working tree (default; validated as an accepted state)
  v<N>     an archived accepted version (also accepts plain <N>)
  best     the mechanically best accepted version (leaderboard top)
  <commit> any git ref/commit (content read via git show)
If the default HEAD is not an accepted state (e.g. a crash commit), report.py falls back to the
last accepted version and says so.

Always writes:
  reports/leaderboard.md      — accepted versions ranked by primary metric
  reports/experiment_log.md   — human-readable ledger of every run (raw ledger: results.tsv)

With --report, also writes:
  reports/research_report.md  — structured human-readable report skeleton. Data-driven sections
    (KPI/version-evolution/train-OOS-full summary tables, benchmark comparison, charts, yearly
    returns with train/OOS annotation, optional factor analysis, cost sensitivity grid on
    OOS+train, overfitting diagnostics, gate check table, experiment process, reproduction path,
    appendices with research.toml and strategy.py) are filled from artifacts; narrative sections
    carry TODO placeholders that the agent completes in the project's report language
    (research.toml -> report.language).
  reports/charts/*.png        — equity, drawdown, yearly returns and rolling Sharpe charts
    (requires matplotlib + pandas in the project environment; skipped with a note if absent).

--publish copies the skeleton to docs/research-report.md (committed location) without overwriting
an existing file.

Benchmark, cost sensitivity and DSR diagnostics require the harness to report a benchmark block in
metrics.json and gross returns in returns.csv (the reference harness does this). Missing artifacts
are skipped gracefully.

The report is not the ledger: results.tsv and reports/experiment_log.md keep the raw flow.
"""

import argparse
import json
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _common as common


I18N = {
    "zh": {
        "title": "研究报告",
        "meta_generated": "生成日期",
        "meta_lang": "报告语言",
        "meta_metric": "主指标",
        "meta_rule": "决策规则",
        "meta_mode": "模式",
        "meta_final": "最终版本来源",
        "summary": "摘要",
        "kpi": "关键指标速览",
        "data": "数据背景与说明",
        "design": "策略设计思想",
        "final": "最终策略：参数设置与规则",
        "findings": "实验/调研中的发现",
        "comparison": "数据对比",
        "sensitivity": "成本与参数敏感性分析",
        "risks": "风险与局限",
        "process": "实验过程记录",
        "usage": "项目复线路径、项目结构与脚本使用说明",
        "repro": "可复现性",
        "todo": "待撰写",
        "col_baseline": "基线",
        "col_final": "最终推荐",
        "col_best": "机械最优",
        "row_metric": "主指标",
        "row_annret": "年化收益",
        "row_calmar": "Calmar 比率",
        "row_dd": "最大回撤",
        "row_turnover": "日均换手",
        "row_exposure": "平均暴露",
        "row_tstat": "t 统计量",
        "kpi_header": "指标",
        "yearly_title": "分年度收益",
        "charts_note": "图表与分年度表由最终版本对应的回测产物生成",
        "benchmark": "基准对比",
        "bench_col": "基准",
        "bench_beta": "Beta",
        "bench_alpha": "Alpha（年化）",
        "bench_ir": "信息比率（IR）",
        "bench_excess": "超额年化收益",
        "cost_grid": "成本敏感性（测试段，离线重算）",
        "cost_current": "← 当前",
        "evo": "版本演进（OOS 机械验收）",
        "evo_desc": "关键改动",
        "col_version": "版本",
        "summary_tbl": "训练 / OOS / 全样本汇总",
        "col_train": "训练",
        "col_oos": "OOS",
        "col_full": "全样本",
        "row_cum": "累计收益",
        "seg_train": "训练",
        "seg_oos": "OOS",
        "yearly_col_seg": "区间",
        "notes_title": "数据可用性说明（自动）",
        "factor": "因子专项分析",
        "factor_ic": "IC",
        "factor_rank_ic": "Rank IC",
        "factor_icir": "ICIR",
        "factor_ls_ann": "多空年化",
        "factor_ls_sharpe": "多空夏普",
        "factor_decay": "Rank IC 衰减",
        "factor_quantiles": "分层表现",
        "factor_horizon": "期数",
        "factor_quantile": "分组",
        "gate": "Gate 对照与结论建议",
        "gate_improve": "主指标相对基线改善",
        "gate_oosis": "OOS/IS 比",
        "gate_dsr": "DSR 启发式",
        "gate_training": "训练/OOS 同向",
        "gate_pass": "✅ 通过",
        "gate_fail": "❌ 未达",
        "gate_col_gate": "Gate",
        "gate_col_std": "标准",
        "gate_col_val": "表现",
        "gate_col_status": "状态",
        "gate_reco": "结论建议（continue / kill / promote）及理由、所需补充证据",
        "appendix_contract": "附录 A：评估契约（research.toml）",
        "appendix_code": "附录 B：策略代码（strategy.py）",
        "publish_done": "已发布：",
        "publish_skip": "已存在，未覆盖（请人工合并）：",
        "note_artifacts": "无法定位最终版本的回测产物（experiments/<run_tag>/），图表与分年度表未生成",
        "note_missing_returns": "缺少 returns.csv/equity.csv，图表与分年度表未生成",
        "note_no_mpl": "未安装 matplotlib 或 pandas，图表未生成（pip install matplotlib pandas 可启用）",
        "note_bench": "metrics.json 未提供 benchmark 块或 bench_* 字段，基准对比已跳过",
        "note_no_yearly": "无分年度数据（既无 returns.csv，metrics.json 也无 yearly/train_yearly）",
        "odiag": "过拟合与稳健性诊断",
        "odiag_runs": "实验总数",
        "odiag_accept": "接受率",
        "odiag_tstat": "最终版本 t 统计量（测试段）",
        "odiag_oosis": "OOS / IS 比",
        "odiag_dsr": "DSR 启发式（Bailey–López de Prado）",
        "odiag_ok": "稳健（≥0.95）",
        "odiag_mid": "中性（0.5–0.95）",
        "odiag_bad": "过拟合风险高（<0.5）",
        "odiag_note": "DSR 为简化启发式：以实验数为试验次数，结合最终版本测试段收益的偏度/峰度与 t 统计量估算；OOS/IS = 测试段主指标 / 训练段主指标，>0 表示样本外方向一致。",
    },
    "en": {
        "title": "Research Report",
        "meta_generated": "generated",
        "meta_lang": "report language",
        "meta_metric": "primary metric",
        "meta_rule": "decision rule",
        "meta_mode": "mode",
        "meta_final": "final version source",
        "summary": "Summary",
        "kpi": "Key Metrics at a Glance",
        "data": "Data Background",
        "design": "Strategy Design Rationale",
        "final": "Final Strategy: Parameters and Rules",
        "findings": "Notable Findings",
        "comparison": "Data Comparison",
        "sensitivity": "Cost and Parameter Sensitivity",
        "risks": "Risks and Limitations",
        "process": "Experiment Process",
        "usage": "Project Layout, Scripts and Reproduction Path",
        "repro": "Reproducibility",
        "todo": "TODO",
        "col_baseline": "baseline",
        "col_final": "final",
        "col_best": "best",
        "row_metric": "primary metric",
        "row_annret": "annual return",
        "row_calmar": "Calmar",
        "row_dd": "max drawdown",
        "row_turnover": "daily turnover",
        "row_exposure": "avg exposure",
        "row_tstat": "t-stat",
        "kpi_header": "metric",
        "yearly_title": "Yearly Returns",
        "charts_note": "charts and the yearly table come from the final version's backtest artifacts",
        "benchmark": "Benchmark Comparison",
        "bench_col": "benchmark",
        "bench_beta": "Beta",
        "bench_alpha": "Alpha (ann.)",
        "bench_ir": "Information Ratio",
        "bench_excess": "Excess Return (ann.)",
        "cost_grid": "Cost Sensitivity (test segment, recomputed offline)",
        "cost_current": "<- current",
        "evo": "Version Evolution (OOS mechanical acceptance)",
        "evo_desc": "key change",
        "col_version": "version",
        "summary_tbl": "Train / OOS / Full-sample Summary",
        "col_train": "train",
        "col_oos": "OOS",
        "col_full": "full",
        "row_cum": "cumulative return",
        "seg_train": "train",
        "seg_oos": "OOS",
        "yearly_col_seg": "segment",
        "notes_title": "Data availability notes (auto)",
        "factor": "Factor Analysis",
        "factor_ic": "IC",
        "factor_rank_ic": "Rank IC",
        "factor_icir": "ICIR",
        "factor_ls_ann": "long-short ann.",
        "factor_ls_sharpe": "long-short Sharpe",
        "factor_decay": "Rank IC Decay",
        "factor_quantiles": "Quantile Performance",
        "factor_horizon": "horizon",
        "factor_quantile": "quantile",
        "gate": "Gate Check and Recommendation",
        "gate_improve": "primary metric vs baseline",
        "gate_oosis": "OOS/IS ratio",
        "gate_dsr": "DSR heuristic",
        "gate_training": "train/OOS same sign",
        "gate_pass": "pass",
        "gate_fail": "fail",
        "gate_col_gate": "Gate",
        "gate_col_std": "standard",
        "gate_col_val": "value",
        "gate_col_status": "status",
        "gate_reco": "recommendation (continue / kill / promote) with reasons and required evidence",
        "appendix_contract": "Appendix A: Evaluation Contract (research.toml)",
        "appendix_code": "Appendix B: Strategy Code (strategy.py)",
        "publish_done": "published:",
        "publish_skip": "already exists, not overwritten (merge manually):",
        "note_artifacts": "cannot locate the final version's backtest artifacts (experiments/<run_tag>/); charts and yearly table skipped",
        "note_missing_returns": "returns.csv/equity.csv missing; charts and yearly table skipped",
        "note_no_mpl": "matplotlib or pandas not installed; charts skipped (pip install matplotlib pandas)",
        "note_bench": "metrics.json has no benchmark block or bench_* fields; benchmark comparison skipped",
        "note_no_yearly": "no yearly data (no returns.csv and no yearly/train_yearly in metrics.json)",
        "odiag": "Overfitting and Robustness Diagnostics",
        "odiag_runs": "total experiments",
        "odiag_accept": "acceptance rate",
        "odiag_tstat": "final version t-stat (test)",
        "odiag_oosis": "OOS / IS ratio",
        "odiag_dsr": "DSR heuristic (Bailey-Lopez de Prado)",
        "odiag_ok": "robust (>=0.95)",
        "odiag_mid": "neutral (0.5-0.95)",
        "odiag_bad": "high overfitting risk (<0.5)",
        "odiag_note": "DSR is a simplified heuristic: trials = number of experiments, using skewness/kurtosis and the final t-stat on test returns. OOS/IS = test primary / train primary, >0 means OOS direction agrees with IS.",
    },
}


def lang_of(config):
    lang = config.get("report", {}).get("language", "zh")
    return lang if lang in I18N else "zh"


def todo(t, hint):
    return (
        f"> {t}：{hint}（用报告语言撰写，完成后删除本提示）"
        if t == "待撰写"
        else f"> {t}: {hint} (write in the report language, then remove this line)"
    )


def metrics_for(project, run_tag):
    path = project / "experiments" / run_tag / "metrics.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def fmt(v, digits=4):
    if v is None:
        return "—"
    try:
        return f"{float(v):.{digits}f}"
    except (TypeError, ValueError):
        return str(v)


def fmt_pct(v):
    if v is None:
        return "—"
    try:
        return f"{float(v):.2%}"
    except (TypeError, ValueError):
        return str(v)


def version_rows(rows):
    """Accepted rows in order with their archive labels (baseline -> v0, keeps -> v1..vN)."""
    out = []
    n = 0
    for r in rows:
        if r["status"] == "baseline":
            out.append(("v0", r))
        elif r["status"] == "keep":
            n += 1
            out.append((f"v{n}", r))
    return out


def find_row_by_commit(rows, ref):
    ref = ref.lower()
    for r in rows:
        if r["commit"].lower().startswith(ref):
            return r
    return None


def read_from_git(project, ref, filename):
    try:
        return common.git(project, "show", f"{ref}:{filename}").stdout
    except Exception:
        return None


def kpi_of(metrics):
    if not metrics:
        return None
    pm = metrics.get("primary_metric") or {}
    aux = metrics.get("auxiliary") or {}
    cons = metrics.get("constraints") or {}
    ann = aux.get("annual_return")
    dd = cons.get("max_drawdown")
    calmar = None
    if isinstance(ann, (int, float)) and isinstance(dd, (int, float)) and dd:
        calmar = ann / dd
    return {
        "metric": pm.get("value"),
        "annual_return": ann,
        "calmar": calmar,
        "max_drawdown": dd,
        "turnover": cons.get("turnover"),
        "exposure": cons.get("exposure"),
        "t_stat": metrics.get("t_stat"),
    }


def test_slice_of(ret_df, metrics):
    """Filter a returns frame to the frozen OOS test segment using metrics periods."""
    import pandas as pd

    if ret_df is None or len(ret_df) == 0:
        return ret_df
    start = None
    periods = (metrics or {}).get("periods") or {}
    test = periods.get("test", "")
    if "/" in test:
        start = test.split("/")[0].strip()
    if not start:
        return ret_df
    try:
        mask = ret_df.index >= pd.Timestamp(start)
    except Exception:
        return ret_df
    return ret_df.loc[mask] if mask.any() else ret_df


def cost_grid_rows(ret_df, metrics, base_bps):
    """Recompute net returns at several cost levels on OOS and train segments."""
    if ret_df is None or "gross" not in ret_df.columns or "position" not in ret_df.columns:
        return None
    import numpy as np

    seg = test_slice_of(ret_df, metrics)
    trn = train_slice_of(ret_df, metrics)
    if seg is None or len(seg) < 2:
        return None
    bps_set = {0, int(round(base_bps / 2)), int(base_bps), int(base_bps * 2), int(base_bps * 4)}
    rows = []
    for bps in sorted(bps_set):
        def calc(part):
            if part is None or len(part) < 2:
                return (None, None, None)
            net = part["gross"] - part["position"].diff().abs().fillna(part["position"].abs()) * bps / 10000.0
            std = net.std()
            sharpe = float(net.mean() / std * np.sqrt(252)) if std > 0 else 0.0
            ann = float((1.0 + net).prod() ** (252 / len(net)) - 1.0) if len(net) else 0.0
            eq = (1.0 + net).cumprod()
            dd = float((eq / eq.cummax() - 1.0).min()) if len(net) else 0.0
            return (sharpe, ann, -dd)

        t_sharpe, t_ann, t_dd = calc(seg)
        _, tr_ann, _ = calc(trn)
        rows.append((bps, t_sharpe, t_ann, t_dd, tr_ann))
    return rows


def _norm_cdf(x):
    import math

    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _inv_norm_cdf(p):
    """Acklam's rational approximation of the inverse standard normal CDF."""
    import math

    if p <= 0.0:
        return -8.2
    if p >= 1.0:
        return 8.2
    a = [
        -3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
        1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00,
    ]
    b = [-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01]
    c = [
        -7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
        -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00,
    ]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00]
    plow, phigh = 0.02425, 0.97575
    if p < plow:
        q = math.sqrt(-2.0 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    elif p <= phigh:
        q = p - 0.5
        r = q * q
        x = (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / (
            ((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0
        )
    else:
        q = math.sqrt(-2.0 * math.log(1.0 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / (
            (((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0
        )
    return x


def dsr_heuristic(returns_series, n_trials):
    """Simplified Deflated Sharpe Ratio (Bailey & Lopez de Prado, 2014).

    Uses the per-period Sharpe, sample skewness/kurtosis and the number of backtested
    hypotheses as trials. A heuristic, not a full strategy-pool derivation.
    """
    import math

    n = len(returns_series)
    if n < 4 or n_trials < 1:
        return None
    std = float(returns_series.std())
    if std == 0:
        return None
    sr = float(returns_series.mean() / std)
    skew = float(returns_series.skew())
    kurt = float(returns_series.kurt()) + 3.0  # standard kurtosis
    gamma = 0.5772156649015329
    z1 = _inv_norm_cdf(1.0 - 1.0 / n_trials)
    z2 = _inv_norm_cdf(1.0 - 1.0 / (n_trials * math.e))
    var_sr0 = (1.0 / n) * (1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr)
    sr0 = math.sqrt(max(var_sr0, 0.0)) * ((1.0 - gamma) * z1 + gamma * z2)
    denom = math.sqrt(max(1.0 - skew * sr + ((kurt - 1.0) / 4.0) * sr * sr, 1e-12))
    return _norm_cdf(((sr - sr0) * math.sqrt(n - 1.0)) / denom)


def train_slice_of(ret_df, metrics):
    """Rows before the frozen OOS test start; None when the split is unknown."""
    import pandas as pd

    if ret_df is None or len(ret_df) == 0:
        return None
    start = None
    periods = (metrics or {}).get("periods") or {}
    test = periods.get("test", "")
    if "/" in test:
        start = test.split("/")[0].strip()
    if not start:
        return None
    try:
        mask = ret_df.index < pd.Timestamp(start)
    except Exception:
        return None
    return ret_df.loc[mask] if mask.any() else None


def test_start_year_of(metrics):
    start = None
    periods = (metrics or {}).get("periods") or {}
    test = periods.get("test", "")
    if "/" in test:
        start = test.split("/")[0].strip()
    if not start:
        return None
    try:
        import datetime

        return datetime.datetime.strptime(start[:10], "%Y-%m-%d").year
    except Exception:
        return None


def full_metrics_of(metrics):
    aux = (metrics or {}).get("auxiliary") or {}
    return {
        "primary": aux.get("full_primary", aux.get("full_sharpe")),
        "annual_return": aux.get("full_annual_return"),
        "max_drawdown": aux.get("full_max_drawdown"),
        "sharpe": aux.get("full_sharpe"),
        "cumulative_return": aux.get("full_cumulative_return"),
    }


def benchmark_block(metrics, config):
    """metrics.json benchmark block, with a fallback to common custom fields."""
    if not metrics:
        return None
    bm = metrics.get("benchmark")
    if isinstance(bm, dict):
        return bm
    aux = metrics.get("auxiliary") or {}
    if "bench_cagr" in aux or "bench_max_dd" in aux:
        cfg = config.get("benchmark", {})
        return {
            "name": cfg.get("name", "harness_benchmark"),
            "annual_return": aux.get("bench_cagr"),
            "max_drawdown": aux.get("bench_max_dd"),
            "source": "custom_fields",
        }
    return None


def yearly_table(ret_df, eq_df, metrics):
    """Yearly returns with train/OOS annotation.

    Prefers returns.csv; falls back to metrics auxiliary yearly/train_yearly
    (list of {year, return, max_dd}) when the frame is unavailable.
    Returns rows of (year, return, max_dd, segment) with segment in OOS/train.
    """
    rows = []
    seg_year = test_start_year_of(metrics)
    if ret_df is not None and len(ret_df) > 0:
        col = "return" if "return" in ret_df.columns else ret_df.columns[0]
        idx = ret_df.index
        vals = ret_df[col]
        eq = eq_df.iloc[:, 0] if eq_df is not None else (1 + vals).cumprod()
        years = sorted(set(d.year for d in idx))
        for y in years:
            mask = idx.year == y
            ret = float((1 + vals[mask]).prod() - 1)
            dd = float((eq[mask] / eq[mask].cummax() - 1).min())
            seg = "OOS" if (seg_year is not None and y >= seg_year) else "train"
            rows.append((y, ret, -dd, seg))
        return rows
    aux = (metrics or {}).get("auxiliary") or {}
    for block, seg in ((aux.get("train_yearly"), "train"), (aux.get("yearly"), "OOS")):
        if isinstance(block, list):
            for item in block:
                if isinstance(item, dict) and "year" in item:
                    rows.append(
                        (int(item["year"]), float(item.get("return", 0.0)), float(item.get("max_dd", 0.0)), seg)
                    )
    rows.sort(key=lambda r: r[0])
    return rows


def evolution_rows(project, version_map):
    rows = []
    for label, r in version_map:
        m = metrics_for(project, r["run_tag"])
        aux = m.get("auxiliary") or {}
        cons = m.get("constraints") or {}
        full = full_metrics_of(m)
        rows.append(
            {
                "label": label,
                "desc": r["description"],
                "oos_metric": (m.get("primary_metric") or {}).get("value"),
                "oos_annual": aux.get("annual_return"),
                "oos_dd": cons.get("max_drawdown"),
                "train_metric": aux.get("train_primary", aux.get("train_sharpe")),
                "full_dd": full.get("max_drawdown"),
            }
        )
    return rows


def summary_rows(metrics):
    """(row_label_key, train, oos, full) tuples; None cells render as em-dash."""
    if not metrics:
        return []
    aux = metrics.get("auxiliary") or {}
    cons = metrics.get("constraints") or {}
    full = full_metrics_of(metrics)
    test_primary = (metrics.get("primary_metric") or {}).get("value")
    return [
        ("annual_return", aux.get("train_annual_return"), aux.get("annual_return"), full.get("annual_return")),
        ("cumulative_return", aux.get("train_cumulative_return"), aux.get("cumulative_return"), full.get("cumulative_return")),
        ("max_drawdown", aux.get("train_max_drawdown"), cons.get("max_drawdown"), full.get("max_drawdown")),
        ("sharpe", aux.get("train_sharpe", aux.get("train_primary")), test_primary, full.get("sharpe")),
    ]


def resolve_final(project, config, rows, final_arg, scored, version_map):
    """Resolve the --final ref to a dict describing the recommended final strategy."""
    best_row = scored[0] if scored else None
    best_label = None
    if best_row is not None:
        best_label = next((lab for lab, r in version_map if r["run_tag"] == best_row["run_tag"]), None)

    ref = (final_arg or "HEAD").strip()

    def build(label, row, strategy_py, research_toml, source):
        return {
            "label": label,
            "run_tag": row["run_tag"],
            "commit": row["commit"],
            "metrics": metrics_for(project, row["run_tag"]),
            "strategy_py": strategy_py,
            "research_toml": research_toml,
            "source": source,
            "warn": "",
        }

    # best: mechanical top
    if ref == "best":
        if best_row is None:
            sys.exit("no accepted runs; cannot use --final best")
        label = best_label or "v?"
        snap = project / "versions" / label
        return build(
            label,
            best_row,
            (snap / "strategy.py").read_text() if snap.exists() else read_from_git(project, best_row["commit"], "strategy.py"),
            (snap / "research.toml").read_text() if snap.exists() else read_from_git(project, best_row["commit"], "research.toml"),
            "best",
        )

    # v<N> / plain N
    if ref.lower().startswith("v") and ref[1:].isdigit() or ref.isdigit():
        label = f"v{int(ref[1:] if ref.lower().startswith('v') else ref)}"
        hit = next(((lab, r) for lab, r in version_map if lab == label), None)
        if hit is None:
            sys.exit(f"unknown final version: {ref} (known: {', '.join(lab for lab, _ in version_map) or 'none'})")
        snap = project / "versions" / label
        if not snap.exists():
            sys.exit(f"version snapshot missing: {snap}")
        return build(label, hit[1], (snap / "strategy.py").read_text(), (snap / "research.toml").read_text(), "version")

    # HEAD (default)
    if ref == "HEAD":
        head = common.short_hash(project)
        row = next((r for r in rows if r["commit"] == head and r["status"] in ("baseline", "keep")), None)
        if row is not None:
            label = next((lab for lab, r in version_map if r["run_tag"] == row["run_tag"]), "v?")
            return build(
                label,
                row,
                (project / "strategy.py").read_text(),
                (project / "research.toml").read_text(),
                "HEAD",
            )
        # fall back to last accepted
        if version_map:
            label, last = version_map[-1]
            snap = project / "versions" / label
            res = build(
                label,
                last,
                (snap / "strategy.py").read_text() if snap.exists() else read_from_git(project, last["commit"], "strategy.py"),
                (snap / "research.toml").read_text() if snap.exists() else read_from_git(project, last["commit"], "research.toml"),
                "HEAD-fallback",
            )
            res["warn"] = (
                f"HEAD ({head}) is not an accepted state (crash/other); report uses last accepted "
                f"version {label} instead."
            )
            return res
        sys.exit("no accepted runs; run --baseline first")

    # git ref / commit
    row = find_row_by_commit(rows, ref)
    if row is not None and row["status"] in ("baseline", "keep"):
        label = next((lab for lab, r in version_map if r["run_tag"] == row["run_tag"]), "v?")
        snap = project / "versions" / label
        res = build(
            label,
            row,
            (snap / "strategy.py").read_text() if snap.exists() else read_from_git(project, ref, "strategy.py"),
            (snap / "research.toml").read_text() if snap.exists() else read_from_git(project, ref, "research.toml"),
            f"ref:{ref}",
        )
        return res
    sp = read_from_git(project, ref, "strategy.py")
    rt = read_from_git(project, ref, "research.toml")
    if sp is None or rt is None:
        sys.exit(f"cannot resolve final ref: {ref}")
    return {
        "label": ref,
        "run_tag": None,
        "commit": ref,
        "metrics": {},
        "strategy_py": sp,
        "research_toml": rt,
        "source": f"ref:{ref}",
        "warn": "",
    }


def make_charts(project, run_dir, charts_dir):
    """Return list of (filename, title) written, or [] when unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        return []
    returns_path = run_dir / "returns.csv"
    equity_path = run_dir / "equity.csv"
    if not returns_path.exists() or not equity_path.exists():
        return []
    ret = pd.read_csv(returns_path, parse_dates=[0], index_col=0)
    eq = pd.read_csv(equity_path, parse_dates=[0], index_col=0)
    if ret.empty:
        return []
    ret_col = "return" if "return" in ret.columns else ret.columns[0]
    charts_dir.mkdir(parents=True, exist_ok=True)
    made = []

    def save(fig, name, title):
        fig.suptitle(title, fontsize=10)
        fig.tight_layout(rect=(0, 0, 1, 0.95))
        path = charts_dir / name
        fig.savefig(path, dpi=110)
        plt.close(fig)
        made.append(name)

    # equity curve
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(eq.index, eq.iloc[:, 0], lw=1.2)
    ax.set_ylabel("cumulative net return")
    ax.grid(alpha=0.3)
    save(fig, "equity.png", "Equity Curve")

    # drawdown
    dd = eq.iloc[:, 0] / eq.iloc[:, 0].cummax() - 1
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.fill_between(dd.index, dd.values, 0, color="crimson", alpha=0.35)
    ax.set_ylabel("drawdown")
    ax.grid(alpha=0.3)
    save(fig, "drawdown.png", "Drawdown")

    # yearly returns
    years = sorted(set(d.year for d in ret.index))
    vals = [float((1 + ret[ret_col][ret.index.year == y]).prod() - 1) for y in years]
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.bar([str(y) for y in years], vals, color=["#2a9d8f" if v >= 0 else "#e76f51" for v in vals])
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("yearly return")
    ax.grid(alpha=0.3, axis="y")
    save(fig, "yearly_returns.png", "Yearly Returns")

    # rolling Sharpe (63d)
    r = ret[ret_col]
    roll = r.rolling(63).mean() / r.rolling(63).std() * (252 ** 0.5)
    fig, ax = plt.subplots(figsize=(8, 3.2))
    ax.plot(roll.index, roll.values, lw=1.0)
    ax.axhline(0, color="black", lw=0.6)
    ax.set_ylabel("rolling Sharpe (63d)")
    ax.grid(alpha=0.3)
    save(fig, "rolling_sharpe.png", "Rolling Sharpe")

    return made


def make_factor_charts(factor, charts_dir):
    """Decay curve + quantile bar charts from the factor block; [] when unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return []
    made = []
    charts_dir.mkdir(parents=True, exist_ok=True)
    decay = factor.get("decay") or []
    if len(decay) > 1:
        xs = [d.get("horizon") for d in decay]
        ys = [d.get("rank_ic") for d in decay]
        if all(x is not None and y is not None for x, y in zip(xs, ys)):
            fig, ax = plt.subplots(figsize=(8, 3.2))
            ax.plot(xs, ys, marker="o", lw=1.2)
            ax.axhline(0, color="black", lw=0.6)
            ax.set_xlabel("horizon")
            ax.set_ylabel("rank IC")
            ax.grid(alpha=0.3)
            fig.suptitle("Rank IC Decay", fontsize=10)
            fig.tight_layout(rect=(0, 0, 1, 0.95))
            fig.savefig(charts_dir / "factor_decay.png", dpi=110)
            plt.close(fig)
            made.append("factor_decay.png")
    quantiles = factor.get("quantiles") or []
    if len(quantiles) > 1:
        names = [q.get("quantile", "?") for q in quantiles]
        vals = [q.get("annual_return") for q in quantiles]
        if all(v is not None for v in vals):
            fig, ax = plt.subplots(figsize=(8, 3.2))
            ax.bar(
                [str(n) for n in names],
                vals,
                color=["#2a9d8f" if v >= 0 else "#e76f51" for v in vals],
            )
            ax.axhline(0, color="black", lw=0.6)
            ax.set_ylabel("annual return")
            ax.grid(alpha=0.3, axis="y")
            fig.suptitle("Quantile Returns", fontsize=10)
            fig.tight_layout(rect=(0, 0, 1, 0.95))
            fig.savefig(charts_dir / "factor_quantiles.png", dpi=110)
            plt.close(fig)
            made.append("factor_quantiles.png")
    return made


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project_dir")
    ap.add_argument("--report", action="store_true", help="write the full research report")
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument(
        "--final",
        default="HEAD",
        help="recommended final strategy: HEAD (default), v<N>, best, or a git ref/commit",
    )
    ap.add_argument(
        "--publish",
        action="store_true",
        help="also copy the skeleton to docs/research-report.md (committed location; never overwrites an existing file)",
    )
    args = ap.parse_args()

    project = Path(args.project_dir).resolve()
    config = common.load_config(project)
    rows = common.read_results(project)
    if not rows:
        print("no experiments recorded yet")
        return

    lang = lang_of(config)
    t = I18N[lang]
    direction = config["decision"]["direction"]
    scored = [r for r in rows if r["status"] in ("baseline", "keep")]
    scored.sort(key=lambda r: float(r["metric"]), reverse=(direction == "higher"))
    version_map = version_rows(rows)
    final = resolve_final(project, config, rows, args.final, scored, version_map)

    counts = {"baseline": 0, "keep": 0, "discard": 0, "crash": 0}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    accepted = counts["keep"] + counts["baseline"]
    total = len(rows)
    accept_rate = 100.0 * accepted / total if total else 0.0
    best = scored[0] if scored else None
    base_row = next((r for r in rows if r["status"] == "baseline"), None)

    (project / "reports").mkdir(parents=True, exist_ok=True)

    # ---- leaderboard -------------------------------------------------------
    leaderboard = [
        f"# Leaderboard - {config['project']['name']}",
        "",
        f"- primary metric: `{config['project']['metric']}` ({direction} is better)",
        f"- data version: `{config['project']['data_version']}`",
        f"- runs: {total} | baseline: {counts['baseline']} | keep: {counts['keep']} | "
        f"discard: {counts['discard']} | crash: {counts['crash']} | accept rate: {accept_rate:.0f}%",
        "",
        "| rank | run_tag | commit | metric | status | description |",
        "|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(scored[: args.top], 1):
        leaderboard.append(
            f"| {i} | {r['run_tag']} | `{r['commit']}` | {float(r['metric']):.4f} | {r['status']} | {r['description']} |"
        )
    leaderboard_text = "\n".join(leaderboard)
    (project / "reports" / "leaderboard.md").write_text(leaderboard_text)
    print(leaderboard_text)

    # ---- human-readable ledger (separate from the report) -------------------
    log_lines = [
        f"# Experiment Log - {config['project']['name']}",
        "",
        f"- runs: {total} | baseline: {counts['baseline']} | keep: {counts['keep']} | "
        f"discard: {counts['discard']} | crash: {counts['crash']} | accept rate: {accept_rate:.0f}%",
        "",
        "| run_tag | commit | metric | status | description |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        log_lines.append(f"| {r['run_tag']} | `{r['commit']}` | {r['metric']} | {r['status']} | {r['description']} |")
    log_lines += ["", "> Raw machine-readable ledger: `results.tsv`."]
    (project / "reports" / "experiment_log.md").write_text("\n".join(log_lines))

    if not args.report:
        print(f"\nexperiment log written to {project / 'reports' / 'experiment_log.md'}")
        return

    # ---- charts + yearly table for the final version ------------------------
    charts_dir = project / "reports" / "charts"
    run_dir = project / "experiments" / final["run_tag"] if final["run_tag"] else None
    charts = []
    notes = []
    try:
        import pandas as pd
    except ImportError:
        pd = None
    try:
        import matplotlib  # noqa: F401

        has_mpl = True
    except ImportError:
        has_mpl = False
    ret = None
    eq = None
    if run_dir is None:
        notes.append(t["note_artifacts"])
    elif not (run_dir / "returns.csv").exists():
        notes.append(t["note_missing_returns"])
    elif pd is None or not has_mpl:
        notes.append(t["note_no_mpl"])
    else:
        charts = make_charts(project, run_dir, charts_dir)
        rp = run_dir / "returns.csv"
        ep = run_dir / "equity.csv"
        ret = pd.read_csv(rp, parse_dates=[0], index_col=0)
        eq = pd.read_csv(ep, parse_dates=[0], index_col=0) if ep.exists() else None
    yearly = yearly_table(ret, eq, final["metrics"])
    if not yearly:
        notes.append(t["note_no_yearly"])
    cost_rows = cost_grid_rows(ret, final["metrics"], float(config["cost"]["bps"])) if ret is not None else None
    ret_final = None
    if ret is not None:
        col = "return" if "return" in ret.columns else ret.columns[0]
        seg = test_slice_of(ret, final["metrics"])
        if seg is not None and len(seg) > 0:
            ret_final = seg[col]
    dsr = dsr_heuristic(ret_final, total) if ret_final is not None else None
    bm = benchmark_block(final["metrics"], config)
    if bm is None:
        notes.append(t["note_bench"])
    factor = (final["metrics"] or {}).get("factor")
    factor = factor if isinstance(factor, dict) else None
    factor_charts = make_factor_charts(factor, charts_dir) if factor is not None and has_mpl else []

    # ---- research report (human-readable) ----------------------------------
    report = [f"# {config['project']['name']} · {t['title']}", ""]
    mode = common.mode_of(config)
    if lang == "zh":
        better = "越高越好" if direction == "higher" else "越低越好"
        report += [
            f"- {t['meta_generated']}: {date.today().isoformat()}",
            f"- {t['meta_lang']}: {lang}",
            f"- {t['meta_metric']}: `{config['project']['metric']}`（{better}）",
            f"- {t['meta_mode']}: `{mode}`",
            f"- {t['meta_rule']}: min_improvement={config['decision']['min_improvement']}, "
            f"min_t_stat={config['decision']['min_t_stat']}",
            f"- {t['meta_final']}: `{args.final}` -> `{final['label']}` ({final['source']})",
        ]
    else:
        report += [
            f"- {t['meta_generated']}: {date.today().isoformat()}",
            f"- {t['meta_lang']}: {lang}",
            f"- {t['meta_metric']}: `{config['project']['metric']}` ({direction} is better)",
            f"- {t['meta_mode']}: `{mode}`",
            f"- {t['meta_rule']}: min_improvement={config['decision']['min_improvement']}, "
            f"min_t_stat={config['decision']['min_t_stat']}",
            f"- {t['meta_final']}: `{args.final}` -> `{final['label']}` ({final['source']})",
        ]
    if final["warn"]:
        report += ["", f"> ⚠️ {final['warn']}", ""]
    best_label = next((lab for lab, r in version_map if r["run_tag"] == best["run_tag"]), None) if best else None
    if best is not None and final["label"] != best_label:
        report += [
            "",
            f"> ℹ️ 最终推荐（`{final['label']}`）与机械最优（`{best_label}`）不同：请说明推荐理由"
            if lang == "zh"
            else f"> ℹ️ final recommendation (`{final['label']}`) differs from the mechanical best (`{best_label}`): state why",
            "",
        ]
    if notes:
        report += ["", f"### {t['notes_title']}", ""]
        for n in notes:
            report.append(f"- {n}")
        report += [""]

    # 1. summary + KPI table
    report += ["", f"## {t['summary']}", ""]
    if best:
        report.append(
            f"- runs: {total}; accepted: {accepted} ({accept_rate:.0f}%); best: {best['metric']} ({best['run_tag']})"
        )
    report.append(f"- final: `{final['label']}` ({final['source']})")
    report += ["", f"### {t['kpi']}", ""]
    kpi_base = kpi_of(metrics_for(project, base_row["run_tag"])) if base_row else None
    kpi_final = kpi_of(final["metrics"])
    kpi_best = kpi_of(metrics_for(project, best["run_tag"])) if best else None
    kpi_rows = [
        (t["row_metric"], "metric"),
        (t["row_annret"], "annual_return"),
        (t["row_calmar"], "calmar"),
        (t["row_dd"], "max_drawdown"),
        (t["row_turnover"], "turnover"),
        (t["row_exposure"], "exposure"),
        (t["row_tstat"], "t_stat"),
    ]
    report += [f"| {t['kpi_header']} | {t['col_baseline']} | {t['col_final']} | {t['col_best']} |", "|---|---|---|---|"]
    for label, key in kpi_rows:
        report.append(
            f"| {label} | {fmt(kpi_base[key] if kpi_base else None)} | "
            f"{fmt(kpi_final[key] if kpi_final else None)} | {fmt(kpi_best[key] if kpi_best else None)} |"
        )
    report += ["", todo(t["todo"], "研究目标、过程概要、核心结论与关键数字（一两段）"), ""]

    # 2. data background
    best_metrics = metrics_for(project, best["run_tag"]) if best else {}
    report += [f"## {t['data']}", ""]
    report.append(f"- data file: `{config['project']['data_file']}`")
    report.append(f"- data version: `{config['project']['data_version']}`")
    report.append(f"- validation split: test fraction {config['validation']['test_fraction']} (frozen OOS)")
    if best_metrics.get("periods"):
        p = best_metrics["periods"]
        report.append(f"- periods: train {p['train']}; test {p['test']}")
    report += ["", todo(t["todo"], "数据来源、清洗/调整口径、宇宙选择、点时间（point-in-time）说明等"), ""]

    # 3. design rationale
    report += [f"## {t['design']}", "", todo(t["todo"], "策略想验证的核心假设、为什么这样做、与同类思路的差异"), ""]

    # 4. final parameters and rules (from the resolved final version)
    report += [f"## {t['final']}", ""]
    report.append(f"- version: `{final['label']}` (source: {final['source']}, commit `{final['commit']}`)")
    report += [
        "",
        todo(t["todo"], "决策流程图（建议用 mermaid 绘制）"),
        "",
        todo(t["todo"], "参数表（模块/参数/取值/含义/取值理由）与策略规则的分步说明"),
        "",
        f"> 完整评估契约与策略代码见 {t['appendix_contract']} 与 {t['appendix_code']}。",
        "",
    ]

    # 5. findings
    keep_rows = [r for r in rows if r["status"] == "keep"]
    report += [f"## {t['findings']}", ""]
    if keep_rows:
        report += ["| # | commit | metric | description |", "|---|---|---|---|"]
        for i, r in enumerate(keep_rows, 1):
            report.append(f"| {i} | `{r['commit']}` | {r['metric']} | {r['description']} |")
        report += [""]
    report += [todo(t["todo"], "每项被接受改进的机制解释、观察到但未采用的线索、意外现象"), ""]

    # 6. comparison + charts + yearly table
    report += [f"## {t['comparison']}", ""]
    if base_row and best:
        delta = float(best["metric"]) - float(base_row["metric"])
        report += [
            "| vs | run_tag | metric |",
            "|---|---|---|",
            f"| baseline | {base_row['run_tag']} | {base_row['metric']} |",
            f"| best | {best['run_tag']} | {best['metric']} |",
            "",
            f"- delta: {delta:+.4f}",
            "",
        ]
    evo = evolution_rows(project, version_map)
    if evo:
        report += ["", f"### {t['evo']}", ""]
        report += [
            f"| {t['col_version']} | {t['evo_desc']} | {t['row_metric']} (OOS) | {t['row_annret']} (OOS) | "
            f"{t['row_dd']} (OOS) | {t['row_metric']} ({t['col_train']}) | {t['row_dd']} ({t['col_full']}) |",
            "|---|---|---|---|---|---|---|",
        ]
        for e in evo:
            report.append(
                f"| `{e['label']}` | {e['desc']} | {fmt(e['oos_metric'])} | {fmt(e['oos_annual'])} | "
                f"{fmt(e['oos_dd'])} | {fmt(e['train_metric'])} | {fmt(e['full_dd'])} |"
            )
        report += [""]
    smry = summary_rows(final["metrics"])
    if smry:
        label_map = {
            "annual_return": t["row_annret"],
            "cumulative_return": t["row_cum"],
            "max_drawdown": t["row_dd"],
            "sharpe": "Sharpe",
        }
        report += ["", f"### {t['summary_tbl']}", ""]
        report += [f"| {t['kpi_header']} | {t['col_train']} | {t['col_oos']} | {t['col_full']} |", "|---|---|---|---|"]
        for key, tr, oos, full in smry:
            report.append(f"| {label_map[key]} | {fmt(tr)} | {fmt(oos)} | {fmt(full)} |")
        report += [""]
    if charts:
        report.append(f"> {t['charts_note']}。")
        for name in charts:
            report.append(f"![{name}](charts/{name})")
        report += [""]
    if yearly:
        seg_label = {"OOS": t["seg_oos"], "train": t["seg_train"]}
        report += [
            f"### {t['yearly_title']}",
            "",
            f"| 年份 | {t['row_annret']} | {t['row_dd']} | {t['yearly_col_seg']} |",
            "|---|---|---|---|",
        ]
        for y, retv, dd, seg in yearly:
            report.append(f"| {y} | {retv:.2%} | {dd:.2%} | {seg_label.get(seg, seg)} |")
        report += [""]
    if bm:
        report += ["", f"### {t['benchmark']}", ""]
        report += [
            f"| {t['kpi_header']} | {t['col_final']}（`{final['label']}`） | "
            f"{t['bench_col']}（`{bm.get('name', 'buy_hold')}`） |",
            "|---|---|---|",
        ]
        report.append(
            f"| {t['row_annret']} | {fmt(kpi_final.get('annual_return') if kpi_final else None)} | {fmt(bm.get('annual_return'))} |"
        )
        report.append(f"| Sharpe | {fmt(kpi_final.get('metric') if kpi_final else None)} | {fmt(bm.get('sharpe'))} |")
        report.append(
            f"| {t['row_dd']} | {fmt(kpi_final.get('max_drawdown') if kpi_final else None)} | {fmt(bm.get('max_drawdown'))} |"
        )
        report.append(f"| {t['bench_beta']} | — | {fmt(bm.get('beta'), 3)} |")
        report.append(f"| {t['bench_alpha']} | — | {fmt(bm.get('alpha_ann'))} |")
        report.append(f"| {t['bench_ir']} | — | {fmt(bm.get('ir'))} |")
        report.append(f"| {t['bench_excess']} | — | {fmt(bm.get('excess_ann'))} |")
        report += [""]
    report += [todo(t["todo"], "分年度/分区间表现、不同成本与滑点假设下的对比、子样本稳定性"), ""]

    # 7. factor analysis (optional; only when the harness provides a factor block)
    if factor:
        report += [f"## {t['factor']}", ""]
        report += ["| 指标 | 值 |", "|---|---|"]
        fm = [
            (t["factor_ic"], factor.get("ic")),
            (t["factor_rank_ic"], factor.get("rank_ic")),
            (t["factor_icir"], factor.get("icir")),
            (t["factor_ls_ann"], factor.get("long_short_annual")),
            (t["factor_ls_sharpe"], factor.get("long_short_sharpe")),
        ]
        for label, v in fm:
            if v is not None:
                report.append(f"| {label} | {fmt(v)} |")
        decay = factor.get("decay") or []
        if len(decay) > 1:
            report += ["", f"### {t['factor_decay']}", "", f"| {t['factor_horizon']} | Rank IC |", "|---|---|"]
            for d in decay:
                if isinstance(d, dict) and d.get("horizon") is not None and d.get("rank_ic") is not None:
                    report.append(f"| {d['horizon']} | {fmt(d['rank_ic'])} |")
        quantiles = factor.get("quantiles") or []
        if len(quantiles) > 1:
            report += [
                "",
                f"### {t['factor_quantiles']}",
                "",
                f"| {t['factor_quantile']} | {t['row_annret']} | {t['row_metric']} |",
                "|---|---|---|",
            ]
            for q in quantiles:
                if isinstance(q, dict) and q.get("quantile") is not None:
                    report.append(f"| {q['quantile']} | {fmt(q.get('annual_return'))} | {fmt(q.get('sharpe'))} |")
        if factor_charts:
            for name in factor_charts:
                report.append(f"![{name}](charts/{name})")
        report += [""]

    # 8. sensitivity
    report += [f"## {t['sensitivity']}", ""]
    if cost_rows:
        report += [
            f"### {t['cost_grid']}",
            "",
            f"| cost bps | {t['col_oos']} Sharpe | {t['col_oos']} {t['row_annret']} | "
            f"{t['col_oos']} {t['row_dd']} | {t['col_train']} {t['row_annret']} |",
            "|---|---|---|---|---|",
        ]
        base_bps = int(config["cost"]["bps"])
        for bps, t_sharpe, t_ann, t_dd, tr_ann in cost_rows:
            mark = f" {t['cost_current']}" if bps == base_bps else ""
            report.append(
                f"| {bps}{mark} | {fmt(t_sharpe, 3)} | {fmt_pct(t_ann)} | {fmt_pct(t_dd)} | {fmt_pct(tr_ann)} |"
            )
        report += [""]
    report += [todo(t["todo"], "成本敏感性、参数敏感性（±10%~20%）、换手率与容量的影响"), ""]

    # 9. overfitting diagnostics
    report += [f"## {t['odiag']}", ""]
    report.append(f"- {t['odiag_runs']}: {total}（接受 {accepted}，{accept_rate:.0f}%）")
    report.append(f"- {t['odiag_accept']}: {accept_rate:.0f}%")
    if kpi_final and kpi_final.get("t_stat") is not None:
        report.append(f"- {t['odiag_tstat']}: {fmt(kpi_final['t_stat'])}")
    else:
        report.append(f"- {t['odiag_tstat']}: —")
    train_metric = None
    if final["metrics"]:
        aux = final["metrics"].get("auxiliary") or {}
        train_metric = aux.get("train_primary", aux.get("train_sharpe"))
    test_metric = kpi_final.get("metric") if kpi_final else None
    if isinstance(train_metric, (int, float)) and isinstance(test_metric, (int, float)) and train_metric != 0:
        report.append(f"- {t['odiag_oosis']}: {test_metric / train_metric:.3f}")
    else:
        report.append(f"- {t['odiag_oosis']}: —")
    if dsr is not None:
        verdict = t["odiag_ok"] if dsr >= 0.95 else (t["odiag_mid"] if dsr >= 0.5 else t["odiag_bad"])
        report.append(f"- {t['odiag_dsr']}: {dsr:.3f}（{verdict}）")
    else:
        report.append(f"- {t['odiag_dsr']}: —")
    report += ["", f"> {t['odiag_note']}", ""]

    # 10. gate check + recommendation
    report += [f"## {t['gate']}", ""]
    report += [
        f"| {t['gate_col_gate']} | {t['gate_col_std']} | {t['gate_col_val']} | {t['gate_col_status']} |",
        "|---|---|---|---|",
    ]
    if base_row and kpi_base and kpi_final and kpi_base.get("metric") is not None and kpi_final.get("metric") is not None:
        min_rel = float(config["decision"]["min_improvement"])
        basev = kpi_base["metric"]
        newv = kpi_final["metric"]
        need = min_rel * abs(basev)
        delta = (newv - basev) if direction == "higher" else (basev - newv)
        ok = delta >= need
        report.append(
            f"| {t['gate_improve']} | >= {need:+.4f} | {fmt(newv)} | {t['gate_pass'] if ok else t['gate_fail']} |"
        )
    for key, spec in config["decision"]["constraints"].items():
        value = (final["metrics"].get("constraints") or {}).get(key)
        limit = float(spec["limit"])
        kind = spec.get("kind", "max")
        ok = None if value is None else (value <= limit if kind == "max" else value >= limit)
        status = t["gate_pass"] if ok is True else (t["gate_fail"] if ok is False else "—")
        report.append(f"| {key} | {kind} {fmt(limit)} | {fmt(value)} | {status} |")
    train_metric = None
    if final["metrics"]:
        aux = final["metrics"].get("auxiliary") or {}
        train_metric = aux.get("train_primary", aux.get("train_sharpe"))
    test_metric = kpi_final.get("metric") if kpi_final else None
    if isinstance(train_metric, (int, float)) and isinstance(test_metric, (int, float)) and train_metric != 0:
        ratio = test_metric / train_metric
        report.append(f"| {t['gate_oosis']} | > 0 | {fmt(ratio)} | {t['gate_pass'] if ratio > 0 else t['gate_fail']} |")
        same = (train_metric >= 0) == (test_metric >= 0)
        report.append(
            f"| {t['gate_training']} | 同号 | {fmt(train_metric)} / {fmt(test_metric)} | "
            f"{t['gate_pass'] if same else t['gate_fail']} |"
        )
    if dsr is not None:
        report.append(
            f"| {t['gate_dsr']} | >= 0.95 | {fmt(dsr, 3)} | {t['gate_pass'] if dsr >= 0.95 else t['gate_fail']} |"
        )
    report += ["", todo(t["todo"], t["gate_reco"]), ""]

    # 11. risks and limitations
    report += [f"## {t['risks']}", "", todo(t["todo"], "过拟合风险、样本外失效风险、容量/流动性限制、数据与代码的已知局限"), ""]

    # 12. experiment process
    report += [f"## {t['process']}", ""]
    report += ["| run_tag | commit | metric | status | description |", "|---|---|---|---|---|"]
    for r in rows:
        report.append(f"| {r['run_tag']} | `{r['commit']}` | {r['metric']} | {r['status']} | {r['description']} |")
    report += ["", "> Full ledger: `results.tsv` and `reports/experiment_log.md`.", ""]

    # 13. usage / reproduction path
    report += [f"## {t['usage']}", ""]
    report += [
        "```",
        "python scripts/init_research.py <project> [--sample-data | --pin-data]",
        'python scripts/run_experiment.py <project> --baseline --message "baseline"',
        'python scripts/run_experiment.py <project> --message "H-<n>: <claim>"',
        "python scripts/check_integrity.py <project>",
        "python scripts/report.py <project> [--report] [--final HEAD|v<N>|best]",
        "```",
        "",
        f"- backtest harness: `{config['experiment']['backtest_cmd']}`",
        f"- allowed files: `{', '.join(config['experiment']['allowed_files'])}`",
        "",
        todo(t["todo"], "从数据准备到复现本报告结论的完整路径；项目结构说明（可参考 SKILL.md 的 Project layout）"),
        "",
    ]

    # 14. reproducibility
    report += [f"## {t['repro']}", ""]
    report.append(f"- data version: `{config['project']['data_version']}`")
    try:
        tags = common.git(project, "tag").stdout.strip()
    except Exception:
        tags = ""
    if tags:
        report.append(f"- git tags: `{tags.replace(chr(10), ', ')}`")
    report += [
        "- version snapshots: `versions/v<N>/` (strategy.py + research.toml + metrics.json + DESCRIPTION.txt)",
        "- per-run artifacts: `experiments/<run_tag>/` (metrics.json, run.log, returns.csv, equity.csv)",
        f"- harness: `{config['experiment']['backtest_cmd']}`",
    ]

    # Appendices (contract + code at the end, body stays readable)
    report += ["", f"## {t['appendix_contract']}", "", "```toml"]
    report.append((final["research_toml"] or "").rstrip())
    report += ["```", "", f"## {t['appendix_code']}", "", "```python"]
    report.append((final["strategy_py"] or "").rstrip())
    report += ["```"]

    path = project / "reports" / "research_report.md"
    path.write_text("\n".join(report))
    print(f"\nresearch report skeleton written to {path}")
    print(f"final version: {final['label']} (source: {final['source']})")
    if charts:
        print(f"charts written to {charts_dir}")
    if args.publish:
        docs = project / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        dest = docs / "research-report.md"
        if dest.exists():
            print(f"{t['publish_skip']} {dest}")
        else:
            shutil.copy2(path, dest)
            print(f"{t['publish_done']} {dest}")
    print("complete every TODO section in the report language before finishing the session")


if __name__ == "__main__":
    main()
