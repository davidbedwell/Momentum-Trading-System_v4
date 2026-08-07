from __future__ import annotations

import pandas as pd

CANONICAL_COLUMNS = ("date", "open", "high", "low", "close", "volume")


def normalize_ohlcv(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize provider-shaped daily/intraday bars into canonical OHLCV.

    This function is intentionally deterministic and interpretation-free.
    """
    if frame.empty:
        raise ValueError("Source frame is empty")

    df = frame.copy()
    df.columns = [str(c).strip().lower() for c in df.columns]

    if "time" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"time": "date"})
    if "timestamp" in df.columns and "date" not in df.columns:
        df = df.rename(columns={"timestamp": "date"})

    missing = [c for c in CANONICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing canonical OHLCV fields after normalization: {missing}")

    out = df.loc[:, CANONICAL_COLUMNS].copy()
    out["date"] = pd.to_datetime(out["date"], utc=True, errors="raise")

    for col in ("open", "high", "low", "close", "volume"):
        out[col] = pd.to_numeric(out[col], errors="raise")

    # Canonical ordering is part of deterministic normalization.
    out = out.sort_values("date", kind="mergesort").reset_index(drop=True)
    return out
