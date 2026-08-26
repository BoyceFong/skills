"""Signal generation for the quant-autoresearch baseline strategy.

Contract (do not change):
    generate_signals(df, params) -> pandas.Series of target positions in [-1, 1],
    one value per row, computed causally from data available at that row only.
    The harness executes positions one bar later and applies costs.
"""

import numpy as np
import pandas as pd


DEFAULT_PARAMS = {
    "momentum_window": 20,
    "max_position": 0.8,
    "vol_scale": False,
    "vol_window": 60,
    "target_vol": 0.15,
}


def generate_signals(df, params=None):
    p = {**DEFAULT_PARAMS, **(params or {})}
    close = df["close"]
    momentum = close.pct_change(p["momentum_window"])
    raw = np.sign(momentum) * p["max_position"]
    if p["vol_scale"]:
        vol = close.pct_change().rolling(p["vol_window"]).std() * np.sqrt(252)
        scale = (p["target_vol"] / vol).clip(0.0, 2.0)
        raw = raw * scale
    return pd.Series(raw.fillna(0.0).clip(-1.0, 1.0), index=df.index, name="position")
