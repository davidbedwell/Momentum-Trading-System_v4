from __future__ import annotations

import json

import pytest

from MTS_V4.generalization_state import (
    GeneralizationDefinition,
    GeneralizationStatus,
    JsonGeneralizationStateLedger,
    apply_rd_generalization_updates,
)


def test_generalization_state_requires_cross_subject_provenance_and_frozen_validation(tmp_path):
    path = tmp_path / "generalization_state.json"
    ledger = JsonGeneralizationStateLedger(path)
    ledger.create(
        GeneralizationDefinition("g1", "normalized condition predicts later behavior", ("equity:AAPL",), ("h1",)),
        rationale="AAPL subject-level tentative proposition",
    )
    with pytest.raises(ValueError, match="at least two subjects"):
        ledger.transition("g1", to_status=GeneralizationStatus.CROSS_SUBJECT_CANDIDATE, rationale="candidate")
    ledger.transition(
        "g1",
        to_status=GeneralizationStatus.CROSS_SUBJECT_CANDIDATE,
        rationale="AMD supplies independent subject evidence",
        evidence_subject_ids=("equity:AMD",),
        supporting_result_ids=("r2",),
    )
    with pytest.raises(ValueError, match="validation_criteria"):
        ledger.transition("g1", to_status=GeneralizationStatus.CROSS_SUBJECT_VALIDATING, rationale="validate")
    ledger.transition(
        "g1",
        to_status=GeneralizationStatus.CROSS_SUBJECT_VALIDATING,
        rationale="freeze cross-subject validation",
        validation_criteria="Predeclared criterion authored by RD",
    )
    with pytest.raises(ValueError, match="validation_trial_ids"):
        ledger.transition("g1", to_status=GeneralizationStatus.CROSS_SUBJECT_VERIFIED, rationale="verified")
    final = ledger.transition(
        "g1",
        to_status=GeneralizationStatus.CROSS_SUBJECT_VERIFIED,
        rationale="RD judges frozen validation satisfied",
        validation_trial_ids=("trial-1", "trial-2"),
        supporting_result_ids=("r3", "r4"),
    )
    assert final.status is GeneralizationStatus.CROSS_SUBJECT_VERIFIED
    reopened = JsonGeneralizationStateLedger(path)
    assert reopened.snapshot("g1") == final
    document = json.loads(path.read_text())
    assert document["policy"]["deterministic_status_inference"] is False


def test_apply_rd_generalization_updates_does_not_infer_science(tmp_path):
    ledger = JsonGeneralizationStateLedger(tmp_path / "state.json")
    applied = apply_rd_generalization_updates(
        research_state={
            "generalization_updates": [
                {
                    "action": "CREATE_SUBJECT_TENTATIVE",
                    "generalization_id": "g2",
                    "proposition": "candidate proposition",
                    "source_subject_ids": ["equity:XOM"],
                    "source_hypothesis_ids": ["hx"],
                    "rationale": "RD-authored tentative state",
                }
            ]
        },
        ledger=ledger,
    )
    assert len(applied) == 1
    assert applied[0].status is GeneralizationStatus.SUBJECT_TENTATIVE
    assert apply_rd_generalization_updates(research_state={"other_state": {}}, ledger=ledger) == ()
