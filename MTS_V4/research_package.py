from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping


class ResearchPackageError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


PREDICTIVE_VERIFICATION_SUCCESS_THRESHOLD = 0.60
PREDICTIVE_STATUS_TENTATIVE = "TENTATIVE"
PREDICTIVE_STATUS_VERIFIED = "VERIFIED"
PREDICTIVE_STATUS_NOT_VERIFIED = "NOT_VERIFIED"


@dataclass(frozen=True, slots=True)
class PredictiveValidationTrialRecord:
    """One blind prediction followed later by outcome evaluation.

    The prediction is locked while Qwen is operating without look-ahead. The
    outcome may then be evaluated using subsequent information because the
    prediction is already immutable. Only completed trials enter the cumulative
    success-rate calculation.
    """

    trial_id: str
    prediction_result_id: str
    prediction_statement: str
    prediction_research_phase: str
    prediction_contains_future_information: bool
    outcome_result_id: str | None = None
    success: bool | None = None
    outcome_contains_future_information: bool | None = None
    created_at: str = field(default_factory=_utc_now)
    completed_at: str | None = None


@dataclass(frozen=True, slots=True)
class PredictiveHypothesisRecord:
    """Frozen predictive proposition plus cumulative blind-verification record.

    RD authors the proposition, success definition, and predeclared minimum trial
    count. Human governance fixes the verification success-rate floor at 0.60.
    After creation the scientific proposition is immutable; only blind prediction
    locks and their later outcome evaluations may accumulate. A materially revised
    proposition requires a new hypothesis_id and therefore a fresh verification
    record.
    """

    hypothesis_id: str
    statement: str
    success_definition: str
    minimum_required_trials: int
    source_result_ids: tuple[str, ...] = ()
    discovered_with_lookahead: bool = False
    verification_requires_no_lookahead: bool = True
    verification_success_threshold: float = PREDICTIVE_VERIFICATION_SUCCESS_THRESHOLD
    status: str = PREDICTIVE_STATUS_TENTATIVE
    trials: tuple[PredictiveValidationTrialRecord, ...] = ()
    success_count: int = 0
    failure_count: int = 0
    success_rate: float | None = None
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip():
            raise ResearchPackageError("predictive hypothesis_id cannot be blank")
        if not self.statement.strip():
            raise ResearchPackageError("predictive hypothesis statement cannot be blank")
        if not self.success_definition.strip():
            raise ResearchPackageError("predictive success_definition cannot be blank")
        if self.minimum_required_trials <= 0:
            raise ResearchPackageError("predictive minimum_required_trials must be positive")
        if self.verification_success_threshold != PREDICTIVE_VERIFICATION_SUCCESS_THRESHOLD:
            raise ResearchPackageError(
                "predictive verification_success_threshold is governed at 0.60"
            )
        if self.status not in {
            PREDICTIVE_STATUS_TENTATIVE,
            PREDICTIVE_STATUS_VERIFIED,
            PREDICTIVE_STATUS_NOT_VERIFIED,
        }:
            raise ResearchPackageError(f"invalid predictive hypothesis status: {self.status}")

    def lock_validation_trial(
        self,
        trial: PredictiveValidationTrialRecord,
    ) -> "PredictiveHypothesisRecord":
        if trial.prediction_research_phase != "VALIDATION":
            raise ResearchPackageError(
                "predictive trial prediction must come from VALIDATION research_phase"
            )
        if trial.prediction_contains_future_information:
            raise ResearchPackageError(
                "predictive trial prediction may not contain look-ahead information"
            )
        if trial.outcome_result_id is not None or trial.success is not None:
            raise ResearchPackageError(
                "new predictive trial must be locked before outcome is recorded"
            )
        if any(item.trial_id == trial.trial_id for item in self.trials):
            raise ResearchPackageError(f"duplicate predictive trial_id: {trial.trial_id}")
        if any(
            item.prediction_result_id == trial.prediction_result_id
            for item in self.trials
        ):
            raise ResearchPackageError(
                "Analysis result already used to lock a predictive trial: "
                f"{trial.prediction_result_id}"
            )
        return replace(
            self,
            trials=self.trials + (trial,),
            updated_at=_utc_now(),
        )

    def record_validation_outcome(
        self,
        *,
        trial_id: str,
        outcome_result_id: str,
        success: bool,
        outcome_contains_future_information: bool,
    ) -> "PredictiveHypothesisRecord":
        matches = [
            index for index, item in enumerate(self.trials) if item.trial_id == trial_id
        ]
        if len(matches) != 1:
            raise ResearchPackageError(
                f"predictive outcome requires exactly one trial match: {trial_id}"
            )
        if any(
            item.outcome_result_id == outcome_result_id
            for item in self.trials
            if item.outcome_result_id is not None
        ):
            raise ResearchPackageError(
                f"Analysis result already used as predictive outcome: {outcome_result_id}"
            )
        index = matches[0]
        existing = self.trials[index]
        if existing.outcome_result_id is not None or existing.success is not None:
            raise ResearchPackageError(
                f"predictive trial outcome already recorded: {trial_id}"
            )
        completed = replace(
            existing,
            outcome_result_id=outcome_result_id,
            success=success,
            outcome_contains_future_information=outcome_contains_future_information,
            completed_at=_utc_now(),
        )
        trials = list(self.trials)
        trials[index] = completed
        completed_trials = [item for item in trials if item.success is not None]
        success_count = sum(1 for item in completed_trials if item.success is True)
        failure_count = len(completed_trials) - success_count
        success_rate = (
            success_count / len(completed_trials) if completed_trials else None
        )
        if len(completed_trials) < self.minimum_required_trials:
            status = PREDICTIVE_STATUS_TENTATIVE
        elif success_rate is not None and success_rate >= self.verification_success_threshold:
            status = PREDICTIVE_STATUS_VERIFIED
        else:
            status = PREDICTIVE_STATUS_NOT_VERIFIED
        return replace(
            self,
            trials=tuple(trials),
            success_count=success_count,
            failure_count=failure_count,
            success_rate=success_rate,
            status=status,
            updated_at=_utc_now(),
        )


@dataclass(frozen=True, slots=True)
class ResearchQuestionRecord:
    question_id: str
    question: str
    rationale: str
    research_phase: str
    parent_question_id: str | None = None
    created_at: str = field(default_factory=_utc_now)


@dataclass(frozen=True, slots=True)
class ResearchAnalysisRecord:
    request_id: str
    question_id: str
    method_id: str
    parameters: Mapping[str, Any]
    evidence_ids: tuple[str, ...]
    analysis_inputs: tuple[Mapping[str, Any], ...]
    result_id: str | None = None
    execution_status: str | None = None
    interpretation: str | None = None
    research_phase: str = "EXPLORATION"
    future_information: Mapping[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_utc_now)


@dataclass(frozen=True, slots=True)
class ResearchPackageStateTransition:
    transition_id: str
    state: Mapping[str, Any]
    created_at: str = field(default_factory=_utc_now)


@dataclass(frozen=True, slots=True)
class ResearchPackage:
    rp_id: str
    subject_id: str
    campaign_id: str
    originating_question: str
    originating_rationale: str
    created_by: str = "AI_RESEARCH_DIRECTOR"
    parent_rp_id: str | None = None
    hypotheses: tuple[Mapping[str, Any], ...] = ()
    predictive_hypotheses: tuple[PredictiveHypothesisRecord, ...] = ()
    questions: tuple[ResearchQuestionRecord, ...] = ()
    analyses: tuple[ResearchAnalysisRecord, ...] = ()
    findings: tuple[Mapping[str, Any], ...] = ()
    unresolved_issues: tuple[Mapping[str, Any], ...] = ()
    state_transitions: tuple[ResearchPackageStateTransition, ...] = ()
    status: str = "OPEN"
    close_reason: str | None = None
    final_assessment: str | None = None
    created_at: str = field(default_factory=_utc_now)
    updated_at: str = field(default_factory=_utc_now)
    version: int = 1

    def _require_open(self) -> None:
        if self.status != "OPEN":
            raise ResearchPackageError(f"research package {self.rp_id} is closed")

    def _evolve(self, **changes: Any) -> "ResearchPackage":
        return replace(
            self,
            **changes,
            updated_at=_utc_now(),
            version=self.version + 1,
        )

    def append_question(self, question: ResearchQuestionRecord) -> "ResearchPackage":
        self._require_open()
        if any(item.question_id == question.question_id for item in self.questions):
            raise ResearchPackageError(f"duplicate question_id: {question.question_id}")
        if question.parent_question_id is not None and not any(
            item.question_id == question.parent_question_id for item in self.questions
        ):
            raise ResearchPackageError(
                f"missing parent_question_id: {question.parent_question_id}"
            )
        return self._evolve(questions=self.questions + (question,))

    def append_analysis(self, analysis: ResearchAnalysisRecord) -> "ResearchPackage":
        self._require_open()
        if any(item.request_id == analysis.request_id for item in self.analyses):
            raise ResearchPackageError(f"duplicate request_id: {analysis.request_id}")
        if not any(item.question_id == analysis.question_id for item in self.questions):
            raise ResearchPackageError(f"missing question_id: {analysis.question_id}")
        return self._evolve(analyses=self.analyses + (analysis,))

    def record_analysis_outcome(
        self,
        *,
        request_id: str,
        result_id: str,
        execution_status: str | None,
        interpretation: str | None,
        future_information: Mapping[str, Any] | None = None,
    ) -> "ResearchPackage":
        self._require_open()
        matches = [index for index, item in enumerate(self.analyses) if item.request_id == request_id]
        if len(matches) != 1:
            raise ResearchPackageError(
                f"analysis outcome requires exactly one request_id match: {request_id}"
            )
        index = matches[0]
        existing = self.analyses[index]
        if existing.result_id is not None and existing.result_id != result_id:
            raise ResearchPackageError(
                f"analysis result_id already recorded for request_id: {request_id}"
            )
        updated = replace(
            existing,
            result_id=result_id,
            execution_status=execution_status,
            interpretation=interpretation,
            future_information=dict(future_information or {}),
        )
        analyses = list(self.analyses)
        analyses[index] = updated
        return self._evolve(analyses=tuple(analyses))

    def append_hypothesis(self, hypothesis: Mapping[str, Any]) -> "ResearchPackage":
        self._require_open()
        return self._evolve(hypotheses=self.hypotheses + (dict(hypothesis),))

    def append_predictive_hypothesis(
        self,
        hypothesis: PredictiveHypothesisRecord,
    ) -> "ResearchPackage":
        self._require_open()
        if any(
            item.hypothesis_id == hypothesis.hypothesis_id
            for item in self.predictive_hypotheses
        ):
            raise ResearchPackageError(
                f"duplicate predictive hypothesis_id: {hypothesis.hypothesis_id}"
            )
        return self._evolve(
            predictive_hypotheses=self.predictive_hypotheses + (hypothesis,)
        )

    def lock_predictive_validation_trial(
        self,
        *,
        hypothesis_id: str,
        trial: PredictiveValidationTrialRecord,
    ) -> "ResearchPackage":
        self._require_open()
        matches = [
            index
            for index, item in enumerate(self.predictive_hypotheses)
            if item.hypothesis_id == hypothesis_id
        ]
        if len(matches) != 1:
            raise ResearchPackageError(
                f"predictive validation requires exactly one hypothesis match: {hypothesis_id}"
            )
        index = matches[0]
        updated = self.predictive_hypotheses[index].lock_validation_trial(trial)
        hypotheses = list(self.predictive_hypotheses)
        hypotheses[index] = updated
        return self._evolve(predictive_hypotheses=tuple(hypotheses))

    def record_predictive_validation_outcome(
        self,
        *,
        hypothesis_id: str,
        trial_id: str,
        outcome_result_id: str,
        success: bool,
        outcome_contains_future_information: bool,
    ) -> "ResearchPackage":
        self._require_open()
        matches = [
            index
            for index, item in enumerate(self.predictive_hypotheses)
            if item.hypothesis_id == hypothesis_id
        ]
        if len(matches) != 1:
            raise ResearchPackageError(
                f"predictive validation requires exactly one hypothesis match: {hypothesis_id}"
            )
        index = matches[0]
        updated = self.predictive_hypotheses[index].record_validation_outcome(
            trial_id=trial_id,
            outcome_result_id=outcome_result_id,
            success=success,
            outcome_contains_future_information=outcome_contains_future_information,
        )
        hypotheses = list(self.predictive_hypotheses)
        hypotheses[index] = updated
        return self._evolve(predictive_hypotheses=tuple(hypotheses))

    def append_finding(self, finding: Mapping[str, Any]) -> "ResearchPackage":
        self._require_open()
        return self._evolve(findings=self.findings + (dict(finding),))

    def append_unresolved_issue(self, issue: Mapping[str, Any]) -> "ResearchPackage":
        self._require_open()
        return self._evolve(unresolved_issues=self.unresolved_issues + (dict(issue),))

    def append_state_transition(
        self, transition: ResearchPackageStateTransition
    ) -> "ResearchPackage":
        self._require_open()
        if any(
            item.transition_id == transition.transition_id
            for item in self.state_transitions
        ):
            raise ResearchPackageError(
                f"duplicate transition_id: {transition.transition_id}"
            )
        return self._evolve(
            state_transitions=self.state_transitions + (transition,)
        )

    def close(self, *, close_reason: str, final_assessment: str | None = None) -> "ResearchPackage":
        self._require_open()
        if not close_reason.strip():
            raise ResearchPackageError("close_reason cannot be blank")
        return self._evolve(
            status="CLOSED",
            close_reason=close_reason,
            final_assessment=final_assessment,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
