from __future__ import annotations

import numpy as np
import pandas as pd


def validate_and_profile_ohlcv(df: pd.DataFrame) -> dict[str, object]:
    """Reject malformed canonical observations and return objective quality facts."""
    duplicate_dates = int(df["date"].duplicated().sum())
    null_counts = {c: int(df[c].isna().sum()) for c in df.columns}
    inf_counts = {
        c: int(np.isinf(df[c].to_numpy(dtype=float)).sum())
        for c in ("open", "high", "low", "close", "volume")
    }

    invalid_high = (
        (df["high"] < df["open"])
        | (df["high"] < df["close"])
        | (df["high"] < df["low"])
    )
    invalid_low = (
        (df["low"] > df["open"])
        | (df["low"] > df["close"])
        | (df["low"] > df["high"])
    )
    negative_volume = df["volume"] < 0
    nonpositive_prices = (df[["open", "high", "low", "close"]] <= 0).any(axis=1)

    failures = {
        "duplicate_dates": duplicate_dates,
        "null_values": sum(null_counts.values()),
        "infinite_values": sum(inf_counts.values()),
        "invalid_high_rows": int(invalid_high.sum()),
        "invalid_low_rows": int(invalid_low.sum()),
        "negative_volume_rows": int(negative_volume.sum()),
        "nonpositive_price_rows": int(nonpositive_prices.sum()),
    }

    if any(failures.values()):
        raise ValueError(f"Malformed canonical OHLCV: {failures}")

    gaps = df["date"].diff().dropna()
    return {
        "status": "PASSED",
        "row_count": int(len(df)),
        "duplicate_dates": 0,
        "null_counts": null_counts,
        "infinite_counts": inf_counts,
        "timestamps_monotonic": bool(df["date"].is_monotonic_increasing),
        "first_observation": df["date"].iloc[0].isoformat(),
        "last_observation": df["date"].iloc[-1].isoformat(),
        "median_timestamp_gap_seconds": (
            float(gaps.dt.total_seconds().median()) if not gaps.empty else None
        ),
    }
