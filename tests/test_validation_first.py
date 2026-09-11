from __future__ import annotations

import pytest

from MTS_V4.validation_first import SubjectResearchPhase, ValidationFirstSubjectGate


def test_validation_first_gate_requires_scored_outcome_before_exploration():
    gate = ValidationFirstSubjectGate(subject_id="MSFT", hypothesis_id="H-AAPL-001")
    assert gate.phase is SubjectResearchPhase.SELECTED
    assert gate.exploration_allowed is False

    with pytest.raises(RuntimeError):
        gate.release_to_exploration()

    gate.lock_prediction(trial_id="trial-1", prediction_result_id="result-prediction")
    assert gate.phase is SubjectResearchPhase.VALIDATION_PREDICTION_LOCKED
    assert gate.exploration_allowed is False

    with pytest.raises(RuntimeError):
        gate.release_to_exploration()

    gate.score_outcome(outcome_result_id="result-outcome", success=True)
    assert gate.phase is SubjectResearchPhase.VALIDATION_SCORED

    gate.release_to_exploration()
    assert gate.phase is SubjectResearchPhase.EXPLORATION_RELEASED
    assert gate.exploration_allowed is True


def test_validation_outcome_cannot_precede_prediction_lock():
    gate = ValidationFirstSubjectGate(subject_id="XOM", hypothesis_id="H-001")
    with pytest.raises(RuntimeError):
        gate.score_outcome(outcome_result_id="outcome", success=False)
