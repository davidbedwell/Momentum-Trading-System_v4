import numpy as np
import pandas as pd
import pytest

from Core.deterministic_computation import execute_computations


def fixture_frame(n: int = 320) -> pd.DataFrame:
    close = pd.Series(np.linspace(100.0, 150.0, n))
    return pd.DataFrame({
        "open": close - 0.2,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.arange(n, dtype=float) + 1000.0,
    })


def test_default_execution_runs_active_families():
    result = execute_computations(fixture_frame())
    assert len(result.data) == 320
    assert set(result.audit["family_id"]) == {
        "PRICE_CANDLE",
        "TREND",
        "MOMENTUM",
        "VOLATILITY",
        "VOLUME_LIQUIDITY",
        "MARKET_STRUCTURE",
    }
    assert result.audit["status"].eq("PASSED").all()


def test_measurement_filter_fails_closed():
    with pytest.raises(KeyError, match="Unknown/unimplemented measurements"):
        execute_computations(
            fixture_frame(),
            measurement_names=["definitely_not_a_measurement"],
        )


def test_missing_ohlcv_fails():
    with pytest.raises(ValueError, match="Missing OHLCV"):
        execute_computations(fixture_frame().drop(columns=["volume"]))
