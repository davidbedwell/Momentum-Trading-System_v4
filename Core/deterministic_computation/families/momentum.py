from __future__ import annotations

import pandas as pd

from ..utils import safe_div, wilder


def _rsi(close: pd.Series, length: int) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    avg_gain = wilder(gains, length)
    avg_loss = wilder(losses, length)
    rs = safe_div(avg_gain, avg_loss)
    return 100.0 - (100.0 / (1.0 + rs))


def calculate(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    close = df["close"]

    for n in (3, 5, 10, 14, 20, 50):
        out[f"roc_{n}"] = close.pct_change(n) * 100.0

    for n in (7, 14, 21):
        out[f"rsi_{n}"] = _rsi(close, n)

    ema12 = close.ewm(span=12, adjust=False, min_periods=12).mean()
    ema26 = close.ewm(span=26, adjust=False, min_periods=26).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    out["macd_line"] = macd
    out["macd_signal"] = signal
    out["macd_histogram"] = macd - signal

    ppo = safe_div(ema12 - ema26, ema26) * 100.0
    ppo_signal = ppo.ewm(span=9, adjust=False, min_periods=9).mean()
    out["ppo_line"] = ppo
    out["ppo_signal"] = ppo_signal
    out["ppo_histogram"] = ppo - ppo_signal

    low14 = df["low"].rolling(14).min()
    high14 = df["high"].rolling(14).max()
    k = 100.0 * safe_div(close - low14, high14 - low14)
    out["stochastic_k_14"] = k
    out["stochastic_d_14"] = k.rolling(3).mean()
    out["williams_r_14"] = -100.0 * safe_div(high14 - close, high14 - low14)

    typical = (df["high"] + df["low"] + close) / 3.0
    mean20 = typical.rolling(20).mean()
    mad20 = typical.rolling(20).apply(
        lambda x: float(abs(x - x.mean()).mean()),
        raw=True,
    )
    out["cci_20"] = safe_div(typical - mean20, 0.015 * mad20)

    return out
