from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import safe_div, true_range, wilder


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    tr = true_range(df)
    close = df["close"]
    returns = close.pct_change()

    out["true_range"] = tr

    for n in (3, 5, 10, 14, 20, 50):
        atr = wilder(tr, n)
        out[f"atr_{n}"] = atr
        out[f"atr_pct_{n}"] = safe_div(atr, close) * 100.0
        out[f"realized_vol_{n}"] = returns.rolling(n).std() * np.sqrt(252.0) * 100.0

    log_hl = np.log(df["high"] / df["low"])
    out["parkinson_variance"] = (log_hl ** 2) / (4.0 * np.log(2.0))

    log_ho = np.log(df["high"] / df["open"])
    log_lo = np.log(df["low"] / df["open"])
    log_co = np.log(df["close"] / df["open"])
    out["garman_klass_variance"] = (
        0.5 * log_hl ** 2 - (2.0 * np.log(2.0) - 1.0) * log_co ** 2
    )
    out["rogers_satchell_variance"] = (
        log_ho * np.log(df["high"] / df["close"])
        + log_lo * np.log(df["low"] / df["close"])
    )

    mid = close.rolling(20).mean()
    std = close.rolling(20).std()
    upper = mid + 2.0 * std
    lower = mid - 2.0 * std
    out["bollinger_mid_20"] = mid
    out["bollinger_upper_20"] = upper
    out["bollinger_lower_20"] = lower
    out["bollinger_width_20"] = safe_div(upper - lower, mid)
    out["bollinger_percent_b_20"] = safe_div(close - lower, upper - lower)

    return out
