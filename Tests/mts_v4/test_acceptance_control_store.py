from __future__ import annotations

from MTS_V4.acceptance_control_store import NEGATIVE_CONTROL_COLUMN, build_negative_control_rows, negative_control_feature_set


def test_negative_control_uses_only_identity_and_date_not_market_values():
    left = {"security_id": "sec-1", "effective_date": "2026-09-10", "eligible": True, "close": 100.0, "return_20__v1": 0.5}
    right = dict(left, close=999.0, return_20__v1=-0.9)
    first = build_negative_control_rows((left,))[0]
    second = build_negative_control_rows((right,))[0]
    assert first == second
    assert set(first) == {"security_id", "effective_date", "eligible", NEGATIVE_CONTROL_COLUMN}
    definition = negative_control_feature_set()
    assert definition.attributes["expected_result_exposed_to_rd"] is False
    assert definition.features[0].attributes["market_measurement_used"] is False
