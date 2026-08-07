from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_OHLCV = ("open", "high", "low", "close", "volume")


def validate_ohlcv(df: pd.DataFrame) -> None:
    missing = [c for c in REQUIRED_OHLCV if c not in df.columns]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {missing}")
    if df.empty:
        raise ValueError("Input is empty.")
    if df.columns.duplicated().any():
        dupes = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate input columns: {dupes}")


def safe_div(numerator, denominator):
    if isinstance(denominator, pd.Series):
        denominator = denominator.replace(0, np.nan)
    else:
        denominator = np.where(np.asarray(denominator) == 0, np.nan, denominator)
    return numerator / denominator


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def wilder(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(
        alpha=1.0 / length,
        adjust=False,
        min_periods=length,
    ).mean()


def wma(series: pd.Series, length: int) -> pd.Series:
    weights = np.arange(1, length + 1, dtype=float)
    return series.rolling(length).apply(
        lambda values: float(np.dot(values, weights) / weights.sum()),
        raw=True,
    )


def rolling_slope(series: pd.Series, length: int) -> pd.Series:
    x = np.arange(length, dtype=float)
    x_centered = x - x.mean()
    denom = float((x_centered ** 2).sum())

    def calc(values: np.ndarray) -> float:
        y = values.astype(float)
        return float((x_centered * (y - y.mean())).sum() / denom)

    return series.rolling(length).apply(calc, raw=True)
