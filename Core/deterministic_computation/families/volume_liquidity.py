from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import rolling_slope, safe_div


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]
    volume = df["volume"].astype(float)
    dollar_volume = close * volume

    out["dollar_volume"] = dollar_volume

    for n in (5, 10, 20, 50):
        mean = volume.rolling(n).mean()
        median = volume.rolling(n).median()
        std = volume.rolling(n).std()
        out[f"volume_mean_{n}"] = mean
        out[f"volume_median_{n}"] = median
        out[f"relative_volume_mean_{n}"] = safe_div(volume, mean)
        out[f"relative_volume_median_{n}"] = safe_div(volume, median)
        out[f"volume_zscore_{n}"] = safe_div(volume - mean, std)

    direction = np.sign(close.diff()).fillna(0.0)
    out["obv"] = (direction * volume).cumsum()

    high_low = (df["high"] - df["low"]).replace(0, np.nan)
    mf_multiplier = ((close - df["low"]) - (df["high"] - close)) / high_low
    mf_volume = mf_multiplier * volume
    out["accumulation_distribution"] = mf_volume.cumsum()
    out["cmf_20"] = safe_div(mf_volume.rolling(20).sum(), volume.rolling(20).sum())

    typical = (df["high"] + df["low"] + close) / 3.0
    raw_mf = typical * volume
    positive = raw_mf.where(typical.diff() > 0, 0.0)
    negative = raw_mf.where(typical.diff() < 0, 0.0).abs()
    ratio = safe_div(positive.rolling(14).sum(), negative.rolling(14).sum())
    out["mfi_14"] = 100.0 - (100.0 / (1.0 + ratio))

    out["rolling_vwap_20"] = safe_div(
        (typical * volume).rolling(20).sum(),
        volume.rolling(20).sum(),
    )
    out["close_vs_vwap_20"] = safe_div(close, out["rolling_vwap_20"]) - 1.0
    out["amihud_illiquidity"] = safe_div(close.pct_change().abs(), dollar_volume)

    # Useful v1 volume-trajectory measurements for the convergence experiment.
    out["volume_trend_slope"] = rolling_slope(volume, 20)
    out["volume_acceleration"] = out["volume_trend_slope"].diff()
    out["dollar_volume_trend"] = rolling_slope(dollar_volume, 20)
    out["relative_dollar_volume"] = safe_div(
        dollar_volume,
        dollar_volume.rolling(20).mean(),
    )
    out["consecutive_volume_increases"] = (
        (volume > volume.shift(1))
        .astype(int)
        .groupby((volume <= volume.shift(1)).cumsum())
        .cumsum()
    )
    out["consecutive_volume_decreases"] = (
        (volume < volume.shift(1))
        .astype(int)
        .groupby((volume >= volume.shift(1)).cumsum())
        .cumsum()
    )

    return out
