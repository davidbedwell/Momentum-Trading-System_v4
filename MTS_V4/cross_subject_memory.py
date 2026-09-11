from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class ScientificMemoryRecord:
    """Compact RD-authored scientific memory safe for cross-subject exposure.

    This record stores scientific interpretation/provenance only. It must never
    contain raw market rows or reusable Analysis payloads.
    """

    record_id: str
    subject_id: str
    kind: str
    summary: str
    rp_id: str | None = None
    finding_id: str | None = None
    hypothesis_id: str | None = None
    result_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    status: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def compact_context(self) -> Mapping[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResearchFrontierState:
    """Durable RD-authored cross-subject scientific working memory."""

    version: int
    summary: str
    open_questions: tuple[str, ...] = ()
    candidate_generalizations: tuple[str, ...] = ()
    contradictions: tuple[str, ...] = ()
    deprioritized_avenues: tuple[str, ...] = ()
    missing_resources: tuple[str, ...] = ()
    source_record_ids: tuple[str, ...] = ()

    def compact_context(self) -> Mapping[str, object]:
        return asdict(self)


class CrossSubjectScientificMemory:
    """Durable-memory interface consumed by RD context construction."""

    def records(self) -> Sequence[ScientificMemoryRecord]:
        raise NotImplementedError

    def frontier(self) -> ResearchFrontierState | None:
        raise NotImplementedError


@dataclass(slots=True)
class InMemoryCrossSubjectScientificMemory(CrossSubjectScientificMemory):
    _records: dict[str, ScientificMemoryRecord] = field(default_factory=dict)
    _frontier: ResearchFrontierState | None = None

    @staticmethod
    def _validate_record(record: ScientificMemoryRecord) -> None:
        if not record.record_id.strip():
            raise ValueError("record_id cannot be blank")
        if not record.subject_id.strip():
            raise ValueError("subject_id cannot be blank")
        if not record.summary.strip():
            raise ValueError("summary cannot be blank")

    def publish(self, record: ScientificMemoryRecord) -> None:
        self.publish_batch((record,))

    def publish_batch(self, records: Sequence[ScientificMemoryRecord]) -> None:
        """Validate a complete RD-authored batch before mutating scientific memory.

        Exact duplicate records are idempotent. Reusing a record_id with different
        content, either within the proposed batch or against durable memory, is an
        objective identity conflict and rejects the whole batch before any record
        is changed. No deterministic code chooses between conflicting scientific
        statements.
        """
        proposed: dict[str, ScientificMemoryRecord] = {}
        for record in records:
            self._validate_record(record)
            duplicate = proposed.get(record.record_id)
            if duplicate is not None and duplicate != record:
                raise ValueError(
                    "scientific memory batch contains record_id with different content: "
                    f"{record.record_id}"
                )
            proposed[record.record_id] = record

        for record_id, record in proposed.items():
            existing = self._records.get(record_id)
            if existing is not None and existing != record:
                raise ValueError(
                    "scientific memory record_id already exists with different content: "
                    f"{record_id}"
                )

        self._records.update(proposed)

    def set_frontier(self, frontier: ResearchFrontierState) -> None:
        if frontier.version < 1:
            raise ValueError("frontier version must be positive")
        if not frontier.summary.strip():
            raise ValueError("frontier summary cannot be blank")
        if self._frontier is not None and frontier.version <= self._frontier.version:
            raise ValueError("frontier version must increase")
        self._frontier = frontier

    def records(self) -> tuple[ScientificMemoryRecord, ...]:
        return tuple(self._records[key] for key in sorted(self._records))

    def frontier(self) -> ResearchFrontierState | None:
        return self._frontier

    def context(self, *, exclude_subject_id: str | None = None) -> Mapping[str, object]:
        records = [
            record.compact_context()
            for record in self.records()
            if exclude_subject_id is None or record.subject_id != exclude_subject_id
        ]
        return {
            "records": records,
            "frontier": self._frontier.compact_context() if self._frontier is not None else None,
            "policy": {
                "authority": "RD_AUTHORED_SCIENTIFIC_CONTEXT",
                "raw_rows_present": False,
                "mandatory_research_agenda": False,
                "rd_may_test_challenge_reformulate_condition_defer_or_ignore": True,
                "deterministic_scientific_ranking": False,
            },
        }
