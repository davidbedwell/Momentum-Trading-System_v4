"""GA7 array preparation: immutable, contiguous, reusable market inputs.

This prepares inputs only. Portfolio simulation remains governed by GA6 parity.
"""
from dataclasses import dataclass
import numpy as np
import pandas as pd

@dataclass(frozen=True)
class MarketArrays:
    dates: tuple
    tickers: tuple
    features: np.ndarray
    opens: np.ndarray
    closes: np.ndarray
    lows: np.ndarray
    dividends: np.ndarray
    splits: np.ndarray
    present: np.ndarray
    eligible: np.ndarray
    sector: np.ndarray
    defense: np.ndarray

def prepare(frame, feature_columns, policy, defense, *, start="2005-09-14", end="2026-09-14"):
    required = {"date", "ticker", "open", "close", "low", "dividends",
                "stock_splits", "sector_name", "security_id", *feature_columns}
    missing = required - set(frame)
    if missing:
        raise ValueError("Missing market columns: " + repr(sorted(missing)))
    df = frame.copy()
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df.date >= start) & (df.date <= end)].sort_values(["date", "ticker"])
    if df.empty or df.duplicated(["date", "ticker"]).any():
        raise ValueError("Empty or duplicate date/ticker bars")
    dates = tuple(sorted(df.date.unique()))
    tickers = tuple(sorted(df.ticker.unique()))
    di = {x: i for i, x in enumerate(dates)}
    ti = {x: i for i, x in enumerate(tickers)}
    shape = (len(dates), len(tickers))
    numeric = {}
    for col in ("open", "close", "low", "dividends", "stock_splits"):
        numeric[col] = np.full(shape, np.nan, dtype=np.float64)
    features = np.full(shape + (len(feature_columns),), np.nan, dtype=np.float64)
    sector = np.full(shape, -1, dtype=np.int16)
    present = np.zeros(shape, dtype=np.bool_)
    eligible = np.zeros(shape, dtype=np.bool_)
    sector_names = {name: i for i, name in enumerate(sorted(df.sector_name.astype(str).unique()))}
    membership = {(str(d)[:10], t): bool(v) for d, t, v in policy["membership"]}
    blocked = {t: set(map(str, days)) for t, days in policy["blocked"].items()}
    veto = {str(d)[:10]: bool(v) for d, v in policy["risk_veto"].items()}
    if any(d not in defense or d not in veto for d in dates):
        raise ValueError("Missing defense or risk-veto coverage")
    for row in df.itertuples(index=False):
        d, t = row.date, row.ticker
        i, j = di[d], ti[t]
        if (d, t) not in membership:
            raise ValueError("Missing membership: " + repr((d, t)))
        present[i, j] = True
        eligible[i, j] = membership[(d, t)] and d not in blocked.get(t, ()) and bool(veto[d])
        sector[i, j] = sector_names[str(row.sector_name)]
        for col in numeric:
            value = getattr(row, col)
            numeric[col][i, j] = 0.0 if col in ("dividends", "stock_splits") and pd.isna(value) else float(value)
        for k, col in enumerate(feature_columns):
            features[i, j, k] = float(getattr(row, col))
    if np.any(~np.isfinite(numeric["open"][present])) or np.any(numeric["open"][present] <= 0):
        raise ValueError("Invalid open price")
    if np.any(~np.isfinite(numeric["close"][present])) or np.any(numeric["close"][present] <= 0):
        raise ValueError("Invalid close price")
    if np.any(~np.isfinite(numeric["low"][present])) or np.any(numeric["low"][present] <= 0):
        raise ValueError("Invalid low price")
    # Rankings are cross-sectional per day and must be computed once.
    for k in range(len(feature_columns)):
        for i in range(len(dates)):
            valid = present[i] & np.isfinite(features[i, :, k])
            if valid.any():
                values = pd.Series(features[i, valid, k])
                features[i, valid, k] = values.rank(pct=True).to_numpy()
    return MarketArrays(dates, tickers, np.ascontiguousarray(features),
        *(np.ascontiguousarray(numeric[c]) for c in ("open", "close", "low", "dividends", "stock_splits")),
        np.ascontiguousarray(present), np.ascontiguousarray(eligible),
        np.ascontiguousarray(sector), np.ascontiguousarray(np.array([bool(defense[d]) for d in dates])))
