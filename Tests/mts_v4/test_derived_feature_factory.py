from datetime import date, timedelta

from MTS_V4.derived_feature_factory import build_matured_outcome_rows, build_predictor_rows, standard_predictor_feature_set


def _rows(security_id: str, multiplier: float):
    start = date(2024, 1, 1)
    rows = []
    for i in range(330):
        close = (100.0 + i * 0.2) * multiplier
        rows.append({
            "security_id": security_id,
            "ticker": security_id,
            "date": (start + timedelta(days=i)).isoformat(),
            "open": close - 0.2,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 1_000_000 + i * 1000,
            "eligible": True,
            "sector_id": "TECH",
            "shares_outstanding": 100_000_000,
        })
    return rows


def test_predictor_factory_populates_complete_versioned_schema_and_cross_sectional_context():
    raw = _rows("AAA", 1.0) + _rows("BBB", 1.2)
    rows = build_predictor_rows(raw)
    feature_set = standard_predictor_feature_set()
    last = [row for row in rows if row["effective_date"] == max(item["effective_date"] for item in rows)]
    assert len(last) == 2
    for row in last:
        assert set(feature_set.feature_columns).issubset(row)
        assert row["return_252__v1"] is not None
        assert row["sma_200__v1"] is not None
        assert row["relative_volume_20__v1"] is not None
        assert row["breadth_above_sma_200__v1"] == 1.0
        assert row["return_252_percentile__v1"] is not None


def test_outcomes_are_separate_and_unmatured_tail_is_null():
    rows = build_matured_outcome_rows(_rows("AAA", 1.0))
    assert rows[0]["forward_return_63__v1"] is not None
    assert rows[-1]["forward_return_1__v1"] is None
    assert rows[-1]["forward_return_63__v1"] is None
