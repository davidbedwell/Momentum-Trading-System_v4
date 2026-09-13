from __future__ import annotations

import numpy as np
import pandas as pd

from ..utils import rolling_slope, safe_div


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]
    high = df["high"]
    low = df["low"]
    volume = df["volume"].astype(float)
    returns = close.pct_change()
    absolute_return = returns.abs()
    dollar_volume = close * volume

    out["dollar_volume"] = dollar_volume
    out["absolute_return"] = absolute_return
    out["intraday_range_pct"] = safe_div(high - low, close)

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

    high_low = (high - low).replace(0, np.nan)
    mf_multiplier = ((close - low) - (high - close)) / high_low
    mf_volume = mf_multiplier * volume
    out["accumulation_distribution"] = mf_volume.cumsum()
    out["cmf_20"] = safe_div(mf_volume.rolling(20).sum(), volume.rolling(20).sum())

    typical = (high + low + close) / 3.0
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

    amihud = safe_div(absolute_return, dollar_volume)
    out["amihud_illiquidity"] = amihud
    amihud_mean_20 = amihud.rolling(20).mean()
    amihud_std_20 = amihud.rolling(20).std()
    out["amihud_illiquidity_mean_20"] = amihud_mean_20
    out["amihud_illiquidity_zscore_20"] = safe_div(amihud - amihud_mean_20, amihud_std_20)

    dollar_volume_mean_20 = dollar_volume.rolling(20).mean()
    dollar_volume_std_20 = dollar_volume.rolling(20).std()
    out["dollar_volume_mean_20"] = dollar_volume_mean_20
    out["dollar_volume_zscore_20"] = safe_div(
        dollar_volume - dollar_volume_mean_20,
        dollar_volume_std_20,
    )
    out["dollar_volume_cv_20"] = safe_div(dollar_volume_std_20, dollar_volume_mean_20)

    positive_high = high.where(high > 0)
    positive_low = low.where(low > 0)
    log_hl = np.log(safe_div(positive_high, positive_low))
    beta = log_hl.pow(2) + log_hl.shift(1).pow(2)
    two_day_high = pd.concat([positive_high, positive_high.shift(1)], axis=1).max(axis=1)
    two_day_low = pd.concat([positive_low, positive_low.shift(1)], axis=1).min(axis=1)
    gamma = np.log(safe_div(two_day_high, two_day_low)).pow(2)
    denominator = 3.0 - 2.0 * np.sqrt(2.0)
    alpha = (
        (np.sqrt(2.0 * beta) - np.sqrt(beta)) / denominator
        - np.sqrt(gamma / denominator)
    ).clip(lower=0.0)
    exp_alpha = np.exp(alpha.clip(upper=50.0))
    out["corwin_schultz_spread_estimate"] = safe_div(
        2.0 * (exp_alpha - 1.0),
        1.0 + exp_alpha,
    )

    # Useful v1 volume-trajectory measurements for the convergence experiment.
    out["volume_trend_slope"] = rolling_slope(volume, 20)
    out["volume_acceleration"] = out["volume_trend_slope"].diff()
    out["dollar_volume_trend"] = rolling_slope(dollar_volume, 20)
    out["relative_dollar_volume"] = safe_div(
        dollar_volume,
        dollar_volume_mean_20,
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
