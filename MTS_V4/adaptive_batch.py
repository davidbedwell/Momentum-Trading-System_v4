from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class SubjectSelection:
    subject_id: str
    rationale: str
    batch_id: str
    position: int

    def __post_init__(self) -> None:
        if not self.subject_id.strip():
            raise ValueError("subject_id cannot be blank")
        if not self.rationale.strip():
            raise ValueError("selection rationale cannot be blank")
        if not self.batch_id.strip():
            raise ValueError("batch_id cannot be blank")
        if self.position < 1:
            raise ValueError("batch position must be positive")


@dataclass(frozen=True, slots=True)
class SubjectRunLedger:
    subject_id: str
    selection_rationale: str
    decisions: int
    analyses_executed: int
    findings_promoted: int
    research_packages: int = 0
    hypotheses_created: int = 0
    validation_trials: int = 0
    representation_repairs: int = 0
    source_failures: int = 0
    close_reason: str | None = None
    api_calls: int | None = None
    prompt_tokens: int | None = None
    cached_tokens: int | None = None
    completion_tokens: int | None = None
    reasoning_tokens: int | None = None
    estimated_api_cost_usd: float | None = None
    elapsed_seconds: float | None = None
    zero_finding_diagnosis: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "decisions",
            "analyses_executed",
            "findings_promoted",
            "research_packages",
            "hypotheses_created",
            "validation_trials",
            "representation_repairs",
            "source_failures",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.findings_promoted == 0 and self.zero_finding_diagnosis is not None and not self.zero_finding_diagnosis.strip():
            raise ValueError("zero_finding_diagnosis cannot be blank")


@dataclass(frozen=True, slots=True)
class BatchLedger:
    batch_id: str
    subjects: tuple[SubjectRunLedger, ...]
    batch_limit: int = 3

    def __post_init__(self) -> None:
        if not self.batch_id.strip():
            raise ValueError("batch_id cannot be blank")
        if self.batch_limit != 3:
            raise ValueError("approved autonomous batch_limit is exactly 3")
        if len(self.subjects) > self.batch_limit:
            raise ValueError("batch exceeds approved autonomous subject limit")
        ids = [item.subject_id for item in self.subjects]
        if len(ids) != len(set(ids)):
            raise ValueError("batch contains duplicate subjects")

    @property
    def requires_review(self) -> bool:
        return len(self.subjects) >= self.batch_limit

    def compact_context(self) -> Mapping[str, object]:
        return {
            "batch_id": self.batch_id,
            "batch_limit": self.batch_limit,
            "requires_review": self.requires_review,
            "subjects": [asdict(item) for item in self.subjects],
        }


@dataclass(frozen=True, slots=True)
class SubjectEligibilityEnvelope:
    """Human-governed objective envelope; RD retains scientific selection authority."""

    approved_subject_ids: frozenset[str] | None = None
    required_available_sources: frozenset[str] = frozenset()

    def objective_defects(
        self,
        *,
        subject_id: str,
        previously_seen: Sequence[str],
        available_sources: Sequence[str] = (),
    ) -> tuple[str, ...]:
        defects: list[str] = []
        if not subject_id.strip():
            defects.append("subject_id is blank")
            return tuple(defects)
        if subject_id in set(previously_seen):
            defects.append(f"subject has already been researched in this adaptive program: {subject_id}")
        if self.approved_subject_ids is not None and subject_id not in self.approved_subject_ids:
            defects.append(f"subject is outside the human-approved research universe: {subject_id}")
        missing = self.required_available_sources - set(available_sources)
        if missing:
            defects.append(f"required sources unavailable: {sorted(missing)}")
        return tuple(defects)


@dataclass(slots=True)
class ThreeSubjectBatchController:
    """Mechanical governance boundary. It does not select scientific subjects."""

    batch_id: str
    eligibility: SubjectEligibilityEnvelope = field(default_factory=SubjectEligibilityEnvelope)
    _selections: list[SubjectSelection] = field(default_factory=list)
    _ledger_rows: list[SubjectRunLedger] = field(default_factory=list)

    BATCH_LIMIT = 3

    def validate_selection(
        self,
        *,
        subject_id: str,
        rationale: str,
        previously_seen: Sequence[str],
        available_sources: Sequence[str] = (),
    ) -> tuple[str, ...]:
        if len(self._selections) >= self.BATCH_LIMIT:
            return ("three-subject autonomous batch limit reached; human review required",)
        defects = list(
            self.eligibility.objective_defects(
                subject_id=subject_id,
                previously_seen=tuple(previously_seen) + tuple(item.subject_id for item in self._selections),
                available_sources=available_sources,
            )
        )
        if not rationale.strip():
            defects.append("RD selection rationale is blank")
        return tuple(defects)

    def accept_selection(self, *, subject_id: str, rationale: str) -> SubjectSelection:
        if len(self._selections) >= self.BATCH_LIMIT:
            raise RuntimeError("three-subject autonomous batch limit reached; human review required")
        selection = SubjectSelection(
            subject_id=subject_id,
            rationale=rationale,
            batch_id=self.batch_id,
            position=len(self._selections) + 1,
        )
        self._selections.append(selection)
        return selection

    def record_run(self, row: SubjectRunLedger) -> None:
        if not any(item.subject_id == row.subject_id for item in self._selections):
            raise ValueError("cannot record run for subject that was not accepted into this batch")
        if any(item.subject_id == row.subject_id for item in self._ledger_rows):
            raise ValueError("subject run already recorded")
        self._ledger_rows.append(row)

    def ledger(self) -> BatchLedger:
        return BatchLedger(batch_id=self.batch_id, subjects=tuple(self._ledger_rows))

    @property
    def requires_review(self) -> bool:
        return len(self._selections) >= self.BATCH_LIMIT
