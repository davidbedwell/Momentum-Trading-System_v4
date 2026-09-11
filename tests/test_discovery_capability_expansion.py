from MTS_V4.bootstrap import build_runtime
from MTS_V4.discovery_methods import (
    ARITHMETIC_METHOD_ID,
    DETERMINISTIC_FAMILY_METHOD_ID,
    arithmetic_transform,
    deterministic_family_measurements,
    discovery_method_catalog,
)


def _ohlcv_rows():
    return (
        {"date": "2026-01-01", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.0, "volume": 1000.0},
        {"date": "2026-01-02", "open": 101.0, "high": 104.0, "low": 100.0, "close": 103.0, "volume": 1200.0},
        {"date": "2026-01-03", "open": 103.0, "high": 105.0, "low": 101.0, "close": 102.0, "volume": 900.0},
        {"date": "2026-01-04", "open": 102.0, "high": 106.0, "low": 101.0, "close": 105.0, "volume": 1400.0},
        {"date": "2026-01-05", "open": 105.0, "high": 107.0, "low": 103.0, "close": 104.0, "volume": 1100.0},
    )


def test_discovery_catalog_exposes_measurement_families_and_arithmetic_without_ranking():
    catalog = discovery_method_catalog()
    ids = {spec.method_id for spec in catalog.all()}

    assert DETERMINISTIC_FAMILY_METHOD_ID in ids
    assert ARITHMETIC_METHOD_ID in ids

    deterministic = catalog.get(DETERMINISTIC_FAMILY_METHOD_ID)
    assert deterministic.metadata["scientific_selection"] == "AI_RESEARCH_DIRECTOR_ONLY"
    assert deterministic.metadata["deterministic_ranking"] is False
    family_ids = {item["family_id"] for item in deterministic.metadata["active_families"]}
    assert "PRICE_CANDLE" in family_ids
    assert "VOLATILITY" in family_ids


def test_runtime_registers_expanded_discovery_capabilities():
    runtime = build_runtime(rd=object())  # type: ignore[arg-type]

    assert runtime.catalog.get(DETERMINISTIC_FAMILY_METHOD_ID).method_id == DETERMINISTIC_FAMILY_METHOD_ID
    assert runtime.catalog.get(ARITHMETIC_METHOD_ID).method_id == ARITHMETIC_METHOD_ID


def test_deterministic_family_measurements_returns_reusable_row_level_dataset():
    result = deterministic_family_measurements(
        {"ohlcv": _ohlcv_rows()},
        {"families": ["PRICE_CANDLE"]},
    )

    assert "return_close" in result["measurement_columns"]
    dataset = result["derived_datasets"]["deterministic_measurements"]
    assert len(dataset) == len(_ohlcv_rows())
    assert dataset[1]["return_close"] is not None
    assert result["derived_dataset_catalog"]["deterministic_measurements"]["row_count"] == len(_ohlcv_rows())


def test_arithmetic_transform_can_create_ratio_or_interaction_feature():
    rows = (
        {"return_close": 0.02, "atr_pct_10": 0.01},
        {"return_close": -0.03, "atr_pct_10": 0.02},
        {"return_close": 0.01, "atr_pct_10": 0.0},
    )
    result = arithmetic_transform(
        {"measurements": rows},
        {
            "left": {"column": "return_close"},
            "right": {"column": "atr_pct_10"},
            "operation": "DIVIDE",
            "output_name": "volatility_normalized_return",
        },
    )

    dataset = result["derived_datasets"]["arithmetic_feature"]
    assert dataset == [
        {"index": 0, "volatility_normalized_return": 2.0},
        {"index": 1, "volatility_normalized_return": -1.5},
    ]
    assert result["excluded_zero_divisor"] == 1
