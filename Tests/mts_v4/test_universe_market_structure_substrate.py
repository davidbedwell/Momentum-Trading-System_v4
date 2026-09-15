from __future__ import annotations

import pytest

from MTS_V4.universe_market_structure_substrate import method_spec, universe_market_structure


def _rows() -> tuple[dict[str, object], ...]:
    rows = []
    for day_index, day in enumerate(("2026-01-02", "2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09")):
        for security_index, security_id in enumerate(("SEC_A", "SEC_B", "SEC_C")):
            sign = 1.0 if security_index != 1 else -1.0
            value = sign * (day_index + 1) / 100.0
            rows.append({
                "security_id": security_id,
                "effective_date": day,
                "eligible": True,
                "return_5__v1": value,
                "return_20__v1": value * 2,
                "return_63__v1": value * 3,
                "return_126__v1": value * 4,
                "return_252__v1": value * 5,
                "return_252_skip_20__v1": value * 4.5,
                "close_to_sma_20__v1": value,
                "close_to_sma_50__v1": value,
                "close_to_sma_200__v1": value,
                "sma20_slope_5__v1": value,
                "rsi_14__v1": 60.0 if value > 0 else 40.0,
                "natr_20__v1": 0.02 + security_index / 100.0,
                "realized_vol_20__v1": 0.2,
                "realized_vol_63__v1": 0.25,
                "relative_volume_20__v1": 1.0 + value,
                "gap_return__v1": value / 4,
                "intraday_return__v1": value / 2,
                "drawdown_252__v1": -abs(value),
                "range_position_20__v1": 0.6,
                "range_position_50__v1": 0.6,
                "range_position_252__v1": 0.6,
                "return_252_percentile__v1": security_index / 2,
                "return_126_percentile__v1": security_index / 2,
                "return_252_skip_20_percentile__v1": security_index / 2,
                "relative_volume_20_percentile__v1": security_index / 2,
                "natr_20_percentile__v1": security_index / 2,
                "sector_return_252_percentile__v1": security_index / 2,
                "breadth_above_sma_200__v1": 2 / 3,
                "breadth_positive_20__v1": 2 / 3,
            })
    return tuple(rows)


def test_builds_as_of_safe_predictor_only_market_structure() -> None:
    outputs = universe_market_structure(
        {"predictors": _rows()},
        {
            "as_of_date": "2026-01-08",
            "as_of_time": "DAILY_CLOSE",
            "security_attributes": {
                "SEC_A": {"ticker": "AAA", "sector_id": "TECH"},
                "SEC_B": {"ticker": "BBB", "sector_id": "FINANCE"},
                "SEC_C": {"ticker": "CCC", "sector_id": "TECH"},
            },
        },
    )

    assert outputs["observation_clock"]["effective_as_of_date"] == "2026-01-08"
    assert outputs["coverage"]["latest_security_count"] == 3
    assert outputs["policy"]["historical_outcomes_consumed"] is False
    assert outputs["policy"]["findings_created"] is False
    assert outputs["current_market_structure"]["breadth"]["breadth_positive_20__v1"] == pytest.approx(2 / 3)
    assert outputs["current_market_structure"]["participation"]["fraction_positive_return_20"] == pytest.approx(2 / 3)
    assert outputs["derived_datasets"]["daily_market_structure_panel"][-1]["fraction_positive_return_20"] == pytest.approx(2 / 3)
    assert set(outputs["current_market_structure"]["sector_measurements"]) == {"FINANCE", "TECH"}
    assert {row["ticker"] for row in outputs["derived_datasets"]["current_security_snapshot"]} == {"AAA", "BBB", "CCC"}


def test_refuses_outcome_columns() -> None:
    rows = list(_rows())
    rows[0] = {**rows[0], "forward_return_5__v1": 0.1}
    with pytest.raises(ValueError, match="prohibits historical outcome"):
        universe_market_structure({"mixed": rows}, {"as_of_time": "DAILY_CLOSE"})


def test_refuses_to_claim_intraday_state_from_daily_evidence() -> None:
    with pytest.raises(ValueError, match="only as_of_time=DAILY_CLOSE"):
        universe_market_structure({"predictors": _rows()}, {"as_of_time": "10:30:00"})


def test_requested_date_after_high_water_mark_is_reported_separately() -> None:
    outputs = universe_market_structure(
        {"predictors": _rows()}, {"as_of_date": "2026-02-01", "as_of_time": "DAILY_CLOSE"}
    )
    assert outputs["observation_clock"]["requested_as_of_date"] == "2026-02-01"
    assert outputs["observation_clock"]["effective_as_of_date"] == "2026-01-09"


def test_catalog_contract_is_predictor_only_neutral_infrastructure() -> None:
    spec = method_spec()
    assert spec.exploration_allowed is True
    assert spec.validation_allowed is False
    assert spec.allows_future_information is False
    assert spec.metadata["scientific_selection"] == "none"
    assert spec.metadata["human_authorized_infrastructure"] is True
