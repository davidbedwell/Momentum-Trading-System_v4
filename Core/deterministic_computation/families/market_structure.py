from __future__ import annotations

import pandas as pd

from ..utils import safe_div


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]

    for n in (5, 10, 20, 50, 100, 252):
        high = df["high"].rolling(n).max()
        low = df["low"].rolling(n).min()
        out[f"rolling_high_{n}"] = high
        out[f"rolling_low_{n}"] = low
        out[f"range_position_{n}"] = safe_div(close - low, high - low)
        out[f"distance_from_high_{n}"] = safe_div(close, high) - 1.0
        out[f"distance_from_low_{n}"] = safe_div(close, low) - 1.0
        out[f"new_high_{n}"] = df["high"] >= high
        out[f"new_low_{n}"] = df["low"] <= low

    return out
