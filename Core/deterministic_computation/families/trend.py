from __future__ import annotations

import pandas as pd

from ..utils import rolling_slope, safe_div, true_range, wilder

MA_WINDOWS = (5, 10, 20, 50, 100, 200)


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]

    for n in MA_WINDOWS:
        sma = close.rolling(n).mean()
        ema = close.ewm(span=n, adjust=False, min_periods=n).mean()
        out[f"sma_{n}"] = sma
        out[f"ema_{n}"] = ema
        out[f"close_vs_sma_{n}"] = safe_div(close, sma) - 1.0
        out[f"close_vs_ema_{n}"] = safe_div(close, ema) - 1.0

    # Explicit, deterministic MA geometry. These are measurements, not signals.
    aligned_up = (
        (out["sma_20"] > out["sma_50"])
        & (out["sma_50"] > out["sma_200"])
    )
    aligned_down = (
        (out["sma_20"] < out["sma_50"])
        & (out["sma_50"] < out["sma_200"])
    )
    out["moving_average_alignment"] = aligned_up.astype(int) - aligned_down.astype(int)
    out["moving_average_spacing"] = (
        (out["sma_20"] - out["sma_50"]).abs()
        + (out["sma_50"] - out["sma_200"]).abs()
    ) / close
    out["moving_average_compression"] = -out["moving_average_spacing"].diff()
    out["moving_average_expansion"] = out["moving_average_spacing"].diff()

    # Preserve the most useful explicit stack facts from v1.
    out["sma_20_over_50"] = out["sma_20"] > out["sma_50"]
    out["sma_50_over_200"] = out["sma_50"] > out["sma_200"]
    out["sma_20_over_50_over_200"] = aligned_up
    out["sma_20_50_spread_pct"] = (safe_div(out["sma_20"], out["sma_50"]) - 1.0) * 100.0
    out["sma_50_200_spread_pct"] = (safe_div(out["sma_50"], out["sma_200"]) - 1.0) * 100.0

    # Linear-regression style slope family.
    out["linear_regression_slope"] = rolling_slope(close, 20)
    out["normalized_slope"] = safe_div(out["linear_regression_slope"], close)
    out["slope_acceleration"] = out["normalized_slope"].diff()
    out["slope_curvature"] = out["slope_acceleration"].diff()

    # ADX / DMI using Wilder smoothing, matching the v1 reference implementation.
    up_move = df["high"].diff()
    down_move = -df["low"].diff()
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    atr14 = wilder(true_range(df), 14)
    plus_di = 100.0 * safe_div(wilder(plus_dm, 14), atr14)
    minus_di = 100.0 * safe_div(wilder(minus_dm, 14), atr14)
    dx = 100.0 * safe_div((plus_di - minus_di).abs(), plus_di + minus_di)
    out["plus_di_14"] = plus_di
    out["minus_di_14"] = minus_di
    out["adx_14"] = wilder(dx, 14)

    return out
