import numpy as np
import pandas as pd

from Core.deterministic_computation import execute_computations


def frame(n: int = 320) -> pd.DataFrame:
    close = pd.Series(np.linspace(100.0, 150.0, n))
    return pd.DataFrame({
        "open": close - 0.2,
        "high": close + 1.0,
        "low": close - 1.0,
        "close": close,
        "volume": np.arange(n, dtype=float) + 1000.0,
    })


def test_sma_20_matches_direct_rolling_mean():
    df = frame()
    out = execute_computations(df, families=["TREND"]).data
    expected = df["close"].rolling(20).mean()
    np.testing.assert_allclose(out["sma_20"], expected, equal_nan=True)


def test_sma_stack_is_objective_boolean_geometry():
    out = execute_computations(frame(), families=["TREND"]).data
    valid = out["sma_200"].notna()
    assert out.loc[valid, "sma_20_over_50_over_200"].all()


def test_dollar_volume_is_close_times_volume():
    df = frame()
    out = execute_computations(df, families=["VOLUME_LIQUIDITY"]).data
    np.testing.assert_allclose(out["dollar_volume"], df["close"] * df["volume"])


def test_true_range_matches_definition():
    df = frame()
    out = execute_computations(df, families=["VOLATILITY"]).data
    prev = df["close"].shift(1)
    expected = pd.concat([
        df["high"] - df["low"],
        (df["high"] - prev).abs(),
        (df["low"] - prev).abs(),
    ], axis=1).max(axis=1)
    np.testing.assert_allclose(out["true_range"], expected, equal_nan=True)


def test_rsi_is_bounded_when_defined():
    out = execute_computations(frame(), families=["MOMENTUM"]).data
    defined = out["rsi_14"].dropna()
    assert ((defined >= 0) & (defined <= 100)).all()


def test_volume_zscore_matches_governed_reference_formula():
    df = frame()
    out = execute_computations(df, families=["VOLUME_LIQUIDITY"]).data
    mean = df["volume"].rolling(20).mean()
    std = df["volume"].rolling(20).std()
    expected = (df["volume"] - mean) / std
    np.testing.assert_allclose(out["volume_zscore_20"], expected, equal_nan=True)
