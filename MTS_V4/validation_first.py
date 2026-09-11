from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SubjectResearchPhase(str, Enum):
    SELECTED = "SELECTED"
    VALIDATION_PREDICTION_LOCKED = "VALIDATION_PREDICTION_LOCKED"
    VALIDATION_SCORED = "VALIDATION_SCORED"
    EXPLORATION_RELEASED = "EXPLORATION_RELEASED"


@dataclass(slots=True)
class ValidationFirstSubjectGate:
    """Mechanical phase gate for subjects doing blind validation before exploration.

    The gate enforces ordering only. It does not choose the hypothesis, subject,
    prediction, outcome interpretation, or exploratory research direction.
    """

    subject_id: str
    hypothesis_id: str
    phase: SubjectResearchPhase = SubjectResearchPhase.SELECTED
    trial_id: str | None = None
    prediction_result_id: str | None = None
    outcome_result_id: str | None = None
    success: bool | None = None

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("subject_id cannot be blank")
        if not self.hypothesis_id.strip():
            raise ValueError("hypothesis_id cannot be blank")

    def lock_prediction(self, *, trial_id: str, prediction_result_id: str) -> None:
        if self.phase is not SubjectResearchPhase.SELECTED:
            raise RuntimeError(f"prediction cannot be locked from phase {self.phase.value}")
        if not trial_id.strip() or not prediction_result_id.strip():
            raise ValueError("trial_id and prediction_result_id must be nonblank")
        self.trial_id = trial_id
        self.prediction_result_id = prediction_result_id
        self.phase = SubjectResearchPhase.VALIDATION_PREDICTION_LOCKED

    def score_outcome(self, *, outcome_result_id: str, success: bool) -> None:
        if self.phase is not SubjectResearchPhase.VALIDATION_PREDICTION_LOCKED:
            raise RuntimeError("validation outcome cannot be scored before prediction lock")
        if not outcome_result_id.strip():
            raise ValueError("outcome_result_id must be nonblank")
        self.outcome_result_id = outcome_result_id
        self.success = bool(success)
        self.phase = SubjectResearchPhase.VALIDATION_SCORED

    def release_to_exploration(self) -> None:
        if self.phase is not SubjectResearchPhase.VALIDATION_SCORED:
            raise RuntimeError(
                "subject cannot enter unrestricted exploration until blind validation is scored"
            )
        self.phase = SubjectResearchPhase.EXPLORATION_RELEASED

    @property
    def exploration_allowed(self) -> bool:
        return self.phase is SubjectResearchPhase.EXPLORATION_RELEASED
