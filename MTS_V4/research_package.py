from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from typing import Any, Mapping


class ResearchPackageError(RuntimeError):
    pass


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
        )
        analyses = list(self.analyses)
        analyses[index] = updated
        return self._evolve(analyses=tuple(analyses))

    def append_hypothesis(self, hypothesis: Mapping[str, Any]) -> "ResearchPackage":
        self._require_open()
        return self._evolve(hypotheses=self.hypotheses + (dict(hypothesis),))

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
