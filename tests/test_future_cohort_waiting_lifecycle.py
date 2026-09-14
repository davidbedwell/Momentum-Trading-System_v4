from __future__ import annotations

import json

import pytest

from MTS_V4.batch_campaign_continuation import (
    ContinuationBaseline,
    RecoveredBatchCampaignContinuation,
)
from MTS_V4.batch_contracts import BatchResearchDecision
from MTS_V4.batch_rd_codec import (
    BatchResearchDecisionCodec,
    BatchResearchDecisionDecodeError,
)
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_spend_guard import SolResearchProgressEstimate


def _progress() -> dict[str, object]:
    return {
        "estimated_percent_complete": 99,
        "estimated_remaining_batches": 5,
        "estimated_remaining_sol_calls": 5,
        "estimate_confidence": "high",
        "estimate_rationale": "Future prospective cohorts remain outstanding.",
    }


def _waiting_payload() -> dict[str, object]:
    return {
        "continue_research": True,
        "waiting_for_future_cohorts": True,
        "research_packages": [],
        "rp_closures": [],
        "promote_findings": [],
        "research_state": {
            "scientific_continuation_state": {
                "active_hypotheses": ["hypothesis:xom:test"],
                "next_decision_dependencies": ["future cohort must mature"],
            }
        },
        "research_progress": _progress(),
        "batch_interpretation": "Historical discovery is frozen; future evidence is required.",
        "close_reason": None,
    }


def test_codec_accepts_future_cohort_wait_without_placeholder_analysis():
    decision = BatchResearchDecisionCodec.decode(json.dumps(_waiting_payload()))

    assert decision.continue_research is True
    assert decision.waiting_for_future_cohorts is True
    assert decision.research_packages == ()
    assert decision.close_reason is None


def test_codec_preserves_executable_package_invariant():
    payload = _waiting_payload()
    payload["waiting_for_future_cohorts"] = False

    with pytest.raises(
        BatchResearchDecisionDecodeError,
        match="continuing executable batched research requires at least one AI-authored Research Package",
    ):
        BatchResearchDecisionCodec.decode(json.dumps(payload))


def test_codec_rejects_placeholder_empty_package_even_while_waiting():
    payload = _waiting_payload()
    payload["research_packages"] = [
        {
            "rp_id": "RP-XOM-WAIT-001",
            "parent_rp_id": None,
            "objective": "Wait for future evidence.",
            "decision_boundary": "Future cohort must mature.",
            "analyses": [],
        }
    ]

    with pytest.raises(
        BatchResearchDecisionDecodeError,
        match="each Research Package must contain at least one analysis",
    ):
        BatchResearchDecisionCodec.decode(json.dumps(payload))


def test_codec_rejects_waiting_as_closed_research():
    payload = _waiting_payload()
    payload["continue_research"] = False
    payload["close_reason"] = "done"

    with pytest.raises(
        BatchResearchDecisionDecodeError,
        match="WAITING_FOR_FUTURE_COHORTS requires continue_research=true",
    ):
        BatchResearchDecisionCodec.decode(json.dumps(payload))


def test_recovered_waiting_decision_is_not_reported_closed():
    decision = BatchResearchDecision(
        continue_research=True,
        waiting_for_future_cohorts=True,
        research_state={
            "scientific_continuation_state": {
                "next_decision_dependencies": ["future cohort must mature"]
            }
        },
        research_progress=SolResearchProgressEstimate(
            estimated_percent_complete=99,
            estimated_remaining_batches=5,
            estimated_remaining_sol_calls=5,
            estimate_confidence="high",
            estimate_rationale="Waiting for future cohorts.",
        ),
    )
    continuation = RecoveredBatchCampaignContinuation.__new__(
        RecoveredBatchCampaignContinuation
    )

    outcome = continuation.continue_from_decision(
        subject=None,  # not touched by the waiting short-circuit
        evidence=(),
        initial_decision=decision,
        prior_results_by_analysis_id={},
        baseline=ContinuationBaseline(
            decisions=8,
            batches_executed=8,
            analyses_executed=191,
            findings_promoted=2,
        ),
    )

    assert outcome.closed is False
    assert outcome.waiting_for_future_cohorts is True
    assert outcome.close_reason is None
    assert outcome.final_decision is decision
    assert outcome.analyses_executed == 191


def test_sol_schema_explicitly_supports_waiting_without_empty_rp():
    messages = SolBatchResearchDirector._batch_messages(
        operation="INTERPRET_BATCH_RESULTS",
        mission="test",
        payload={},
    )
    body = json.loads(messages[-1]["content"])

    assert "waiting_for_future_cohorts" in body["required_batch_decision_schema"]
    instructions = "\n".join(body["instructions"])
    assert "waiting_for_future_cohorts=true" in instructions
    assert "research_packages=[]" in instructions
    assert "Do not invent placeholder analyses" in instructions
