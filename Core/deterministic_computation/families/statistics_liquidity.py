from __future__ import annotations

import pandas as pd

from ..utils import rolling_slope, safe_div


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    """Explicitly named rolling return statistics from the v1 reference.

    Generic bank names such as `rolling_mean` are intentionally not emitted
    because their input variable/window is not yet governed.
    """
    out = pd.DataFrame(index=df.index)
    close = df["close"]
    returns = close.pct_change()
    dollar_volume = close * df["volume"]
    out["amihud_illiquidity_reference"] = safe_div(returns.abs(), dollar_volume)

    for n in (5, 10, 20, 30, 60, 120, 252):
        roll = returns.rolling(n)
        out[f"return_mean_{n}"] = roll.mean()
        out[f"return_median_{n}"] = roll.median()
        out[f"return_std_{n}"] = roll.std()
        out[f"return_skew_{n}"] = roll.skew()
        out[f"return_kurt_{n}"] = roll.kurt()
        out[f"return_zscore_{n}"] = safe_div(returns - roll.mean(), roll.std())
        out[f"close_slope_{n}"] = rolling_slope(close, n)
        out[f"dollar_volume_median_{n}"] = dollar_volume.rolling(n).median()

    return out
