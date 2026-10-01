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
        assert row["return_252_skip_20__v1"] is not None
        assert row["return_252_skip_20_percentile__v1"] is not None
        assert row["sma_200__v1"] is not None
        assert row["relative_volume_20__v1"] is not None
        assert row["breadth_above_sma_200__v1"] == 1.0
        assert row["return_252_percentile__v1"] is not None


def test_outcomes_are_separate_and_unmatured_tail_is_null():
    rows = build_matured_outcome_rows(_rows("AAA", 1.0))
    assert rows[0]["forward_return_63__v1"] is not None
    assert rows[-1]["forward_return_1__v1"] is None
    assert rows[-1]["forward_return_63__v1"] is None


def test_skipped_month_momentum_excludes_most_recent_twenty_sessions():
    raw = _rows("AAA", 1.0)
    rows = build_predictor_rows(raw)
    row = rows[252]
    expected = raw[232]["close"] / raw[0]["close"] - 1.0
    assert row["return_252_skip_20__v1"] == expected
    assert rows[251]["return_252_skip_20__v1"] is None


def test_expanded_search_features_are_present_and_point_in_time():
    raw = _rows("AAA", 1.0)
    rows = build_predictor_rows(raw)
    row = rows[300]
    expected_prior_high20 = max(item["high"] for item in raw[280:300])
    assert row["prior_high_break_distance_20__v1"] == raw[300]["close"] / expected_prior_high20 - 1.0
    assert row["sma50_slope_10__v1"] is not None
    assert row["sma200_slope_20__v1"] is not None
    assert row["trend_above_sma200_duration__v1"] > 0
    assert row["pullback_from_high_20__v1"] is not None
    assert row["range_width_ratio_20_63__v1"] is not None
    assert row["price_zscore_20__v1"] is not None
    assert row["signed_return_streak__v1"] > 0
    assert row["volatility_ratio_20_63__v1"] is not None
    assert row["dollar_volume__v1"] == raw[300]["close"] * raw[300]["volume"]
    assert row["dollar_volume_relative_20__v1"] is not None
    assert row["amihud_illiquidity_20__v1"] is not None


def test_prior_high_break_feature_excludes_current_session_high():
    raw = _rows("AAA", 1.0)
    raw[300]["high"] = raw[300]["close"] * 10.0
    rows = build_predictor_rows(raw)
    row = rows[300]
    expected = raw[300]["close"] / max(item["high"] for item in raw[280:300]) - 1.0
    assert row["prior_high_break_distance_20__v1"] == expected


def test_remaining_ohlcv_search_vocabulary_is_populated():
    raw = _rows("AAA", 1.0) + _rows("BBB", 1.2)
    rows = build_predictor_rows(raw)
    latest = [r for r in rows if r["effective_date"] == max(x["effective_date"] for x in rows)]
    required = (
        "adx_14__v1","compression_duration__v1","volatility_contraction_duration__v1",
        "volatility_expansion_transition__v1","high_low_spread_proxy__v1",
        "volume_slope_20__v1","up_down_volume_balance_20__v1","exhaustion_score__v1",
        "relative_strength_change_20__v1","sector_vs_universe_return_63__v1",
        "advance_decline_breadth__v1","new_high_low_breadth_252__v1",
        "realized_vol_20_percentile__v1",
    )
    for row in latest:
        for column in required:
            assert column in row
        assert row["adx_14__v1"] is not None
        assert row["high_low_spread_proxy__v1"] is not None
        assert row["relative_strength_change_20__v1"] is not None
