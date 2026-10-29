import pandas as pd
import pytest

from Engines.Intake.normalize import normalize_ohlcv


def test_normalization_is_deterministic_and_sorted():
    raw = pd.DataFrame({
        "timestamp": ["2025-01-02", "2025-01-01"],
        "open": [2, 1],
        "high": [3, 2],
        "low": [1, 0.5],
        "close": [2.5, 1.5],
        "volume": [200, 100],
    })
    a = normalize_ohlcv(raw)
    b = normalize_ohlcv(raw)
    pd.testing.assert_frame_equal(a, b)
    assert a["date"].is_monotonic_increasing
    assert list(a.columns) == ["date", "open", "high", "low", "close", "volume"]


def test_missing_required_field_fails():
    raw = pd.DataFrame({
        "date": ["2025-01-01"],
        "open": [1],
        "high": [2],
        "low": [0.5],
        "close": [1.5],
    })
    with pytest.raises(ValueError, match="Missing canonical OHLCV"):
        normalize_ohlcv(raw)
