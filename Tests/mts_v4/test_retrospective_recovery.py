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

    assert context["policy"]["historical_exposure_status"] == "EXPOSED"
    assert context["policy"]["research_phase"] == "EXPLORATION"
    assert context["policy"]["blind_validation_claim_allowed"] is False
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


def test_recovery_system_message_preserves_batch_and_no_blind_rules() -> None:
    messages = SolRetrospectiveRecoveryResearchDirector._batch_messages(
        operation="BEGIN_BATCH_RESEARCH",
        mission="test mission",
        payload={"retrospective_recovery_context": {"policy": {}}},
    )
    system = messages[0]["content"]
    assert "RETROSPECTIVE RECOVERY" in system
    assert "MUST NEVER be described or counted as blind validation" in system
    assert "author all analyses that are justified now in the same batch" in system
    assert "receive the consolidated batch report" in system
    assert "genuinely unexposed evidence" in system
