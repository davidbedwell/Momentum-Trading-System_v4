from __future__ import annotations

import pytest

from MTS_V4.openrouter_scientific_ladder import (
    INDEPENDENT_JUDGE,
    MODEL_LADDER,
    LadderPolicyError,
    next_model,
    usage_cost_usd,
    validate_independent_assessment,
    validate_live_catalog_entry,
)


def _assessment(model: str, grade: str = "PASS"):
    controls = (
        "cross_sectional_medium_term_momentum",
        "deterministic_negative_control",
        "medium_term_trend_persistence",
        "post_earnings_behavior",
        "short_horizon_reversal",
    )
    return {
        "format": "MTS_V4_INDEPENDENT_FIVE_CONTROL_ASSESSMENT_V1",
        "model": model,
        "review_artifact_sha256": "a" * 64,
        "candidate_self_assessment": False,
        "independent_assessor": "independent-human-chatgpt-review",
        "grades": [{"control_id": item, "grade": grade} for item in controls],
    }


def test_success_requires_all_five_pass() -> None:
    document = _assessment(MODEL_LADDER[0].model)
    document["grades"][4]["grade"] = "PARTIAL"
    result = validate_independent_assessment(
        document,
        expected_model=MODEL_LADDER[0].model,
        expected_review_sha256="a" * 64,
    )
    assert result["all_five_pass"] is False


def test_five_pass_stops_ladder() -> None:
    result = validate_independent_assessment(
        _assessment(MODEL_LADDER[0].model),
        expected_model=MODEL_LADDER[0].model,
        expected_review_sha256="a" * 64,
    )
    assert result["all_five_pass"] is True
    assert next_model([result]) is None


def test_partial_advances_to_next_model() -> None:
    document = _assessment(MODEL_LADDER[0].model, grade="PARTIAL")
    result = validate_independent_assessment(
        document,
        expected_model=MODEL_LADDER[0].model,
        expected_review_sha256="a" * 64,
    )
    assert next_model([result]) == MODEL_LADDER[1].model


def test_candidate_cannot_grade_itself() -> None:
    document = _assessment(MODEL_LADDER[0].model)
    document["candidate_self_assessment"] = True
    with pytest.raises(LadderPolicyError, match="self-assessment"):
        validate_independent_assessment(
            document,
            expected_model=MODEL_LADDER[0].model,
            expected_review_sha256="a" * 64,
        )


def test_live_price_increase_fails_closed() -> None:
    candidate = MODEL_LADDER[0]
    entry = {
        "id": candidate.model,
        "canonical_slug": candidate.model + "-snapshot",
        "context_length": 1_000_000,
        "supported_parameters": ["response_format", "structured_outputs"],
        "pricing": {"prompt": "0.01", "completion": "0.01"},
    }
    with pytest.raises(LadderPolicyError, match="price exceeds"):
        validate_live_catalog_entry(candidate, entry)


def test_usage_cost_uses_governed_ceiling_when_direct_cost_absent() -> None:
    candidate = MODEL_LADDER[0]
    cost = usage_cost_usd(
        {"prompt_tokens": 10_000, "completion_tokens": 1_000}, candidate
    )
    assert cost == pytest.approx(
        10_000 * candidate.maximum_prompt_usd_per_token
        + 1_000 * candidate.maximum_completion_usd_per_token
    )


def test_independent_judge_is_not_a_candidate() -> None:
    assert INDEPENDENT_JUDGE.model == "openai/gpt-5.6-sol"
    assert INDEPENDENT_JUDGE.model not in {item.model for item in MODEL_LADDER}
