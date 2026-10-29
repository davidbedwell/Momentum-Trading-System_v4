from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import safe_div


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    prev_close = c.shift(1)

    out["return_close"] = c.pct_change()
    out["return_log"] = np.log(c / prev_close)
    out["return_intraday"] = c / o - 1.0
    out["return_overnight"] = o / prev_close - 1.0
    out["gap_pct"] = (o / prev_close - 1.0) * 100.0

    out["bar_range"] = h - l
    out["bar_range_pct"] = safe_div(out["bar_range"], prev_close) * 100.0
    out["body"] = c - o
    out["body_abs"] = out["body"].abs()
    out["body_pct"] = safe_div(out["body"], o) * 100.0
    out["upper_wick"] = h - pd.concat([o, c], axis=1).max(axis=1)
    out["lower_wick"] = pd.concat([o, c], axis=1).min(axis=1) - l

    out["body_to_range"] = safe_div(out["body_abs"], out["bar_range"])
    out["upper_wick_to_range"] = safe_div(out["upper_wick"], out["bar_range"])
    out["lower_wick_to_range"] = safe_div(out["lower_wick"], out["bar_range"])
    out["close_location"] = safe_div(c - l, out["bar_range"])
    out["open_location"] = safe_div(o - l, out["bar_range"])

    out["higher_high"] = h > h.shift(1)
    out["higher_low"] = l > l.shift(1)
    out["lower_high"] = h < h.shift(1)
    out["lower_low"] = l < l.shift(1)
    out["inside_bar"] = (h < h.shift(1)) & (l > l.shift(1))
    out["outside_bar"] = (h > h.shift(1)) & (l < l.shift(1))

    prev_o = o.shift(1)
    prev_c = c.shift(1)
    out["bullish_engulfing"] = (
        (c > o)
        & (prev_c < prev_o)
        & (o <= prev_c)
        & (c >= prev_o)
    )
    out["bearish_engulfing"] = (
        (c < o)
        & (prev_c > prev_o)
        & (o >= prev_c)
        & (c <= prev_o)
    )

    overlap = pd.concat([h, h.shift(1)], axis=1).min(axis=1) - pd.concat(
        [l, l.shift(1)], axis=1
    ).max(axis=1)
    prior_range = h.shift(1) - l.shift(1)
    out["range_overlap_prior"] = safe_div(overlap.clip(lower=0), prior_range)

    return out
