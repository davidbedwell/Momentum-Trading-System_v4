from __future__ import annotations

import json
from pathlib import Path

import pytest

from MTS_V4.retrospective_recovery import (
    SolRetrospectiveRecoveryResearchDirector,
    load_retrospective_subject_context,
)


def test_load_retrospective_subject_context_marks_history_exposed(tmp_path: Path) -> None:
    subject = tmp_path / "AMZN"
    (subject / "research_packages").mkdir(parents=True)
    (subject / "rd_decisions.jsonl").write_text(
        json.dumps({"decision": {"continue_research": True}}) + "\n",
        encoding="utf-8",
    )
    (subject / "research_nexus.json").write_text(
        json.dumps({"format": "MTS_V4_RESEARCH_NEXUS_V1"}),
        encoding="utf-8",
    )
    (subject / "subject_ledger.json").write_text(
        json.dumps({"subject_id": "equity:AMZN"}),
        encoding="utf-8",
    )
    (subject / "research_packages" / "RP-OLD.json").write_text(
        json.dumps({"rp_id": "RP-OLD", "subject_id": "equity:AMZN"}),
        encoding="utf-8",
    )

    context = load_retrospective_subject_context(subject)

    policy = context["policy"]
    assert policy["historical_exposure_status"] == "EXPOSED"
    assert policy["research_phase"] == "EXPLORATION"
    assert policy["blind_validation_claim_allowed"] is False
    assert "only when the AI Research Director explicitly authors" in policy[
        "analysis_execution_authority"
    ]
    assert "Deterministic code must not infer, require, schedule, or manufacture re-analysis" in policy[
        "analysis_execution_authority"
    ]
    assert policy["batch_execution_rule"].startswith(
        "If and only if the AI Research Director authors additional Analysis Specifications"
    )

    preserved = context["preserved_state"]
    assert len(preserved["rd_decisions"]) == 1
    assert "research_nexus" in preserved
    assert "subject_ledger" in preserved
    assert "RP-OLD.json" in preserved["research_packages"]


def test_load_retrospective_subject_context_rejects_empty_directory(tmp_path: Path) -> None:
    subject = tmp_path / "EMPTY"
    subject.mkdir()
    with pytest.raises(RuntimeError, match="no preserved retrospective subject state"):
        load_retrospective_subject_context(subject)


def test_recovery_system_message_preserves_sol_only_analysis_authority() -> None:
    messages = SolRetrospectiveRecoveryResearchDirector._batch_messages(
        operation="BEGIN_BATCH_RESEARCH",
        mission="test mission",
        payload={"retrospective_recovery_context": {"policy": {}}},
    )
    system = messages[0]["content"]

    assert "RETROSPECTIVE RECOVERY" in system
    assert "MUST NEVER be described or counted as blind validation" in system
    assert "Retrospective recovery does NOT itself require additional Analysis" in system
    assert "Deterministic code must not infer, require, schedule, or manufacture re-analysis" in system
    assert "Only if YOU, the AI Research Director" in system
    assert "author all analyses justified now in the same batch" in system
    assert "receive the consolidated batch report" in system
    assert "without unnecessary re-analysis" in system
    assert "genuinely unexposed evidence" in system


def test_recovery_system_message_allows_zero_analysis_resolution() -> None:
    messages = SolRetrospectiveRecoveryResearchDirector._batch_messages(
        operation="BEGIN_BATCH_RESEARCH",
        mission="test mission",
        payload={"retrospective_recovery_context": {"policy": {}}},
    )
    system = messages[0]["content"]

    assert "preserved record and presently available evidence are already sufficient" in system
    assert "freeze the tentative predictive hypothesis or close the subject" in system
