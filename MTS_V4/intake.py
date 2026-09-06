from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Protocol

from .cache import TemporaryResearchCache
from .contracts import EvidenceDescriptor, SubjectMetadata


@dataclass(frozen=True, slots=True)
class IntakePayload:
    payload: object
    evidence_type: str
    artifact_type: str
    source_identity: str
    coverage_start: str | None
    coverage_end: str | None
    row_count: int | None
    schema: tuple[str, ...]
    provenance: Mapping[str, Any]
    neutral_semantics: str


class EvidenceSource(Protocol):
    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]: ...


class IntakeEngine:
    """Acquire, validate minimally, describe neutrally, and stage evidence.

    Intake does not decide scientific relevance or meaning.
    """

    def __init__(self, cache: TemporaryResearchCache) -> None:
        self._cache = cache
        self._sequence = 0

    def ingest(
        self,
        *,
        subject: SubjectMetadata,
        source: EvidenceSource,
    ) -> tuple[EvidenceDescriptor, ...]:
        descriptors: list[EvidenceDescriptor] = []
        for payload in source.acquire(subject):
            self._sequence += 1
            evidence_id = f"evidence:{subject.subject_id}:{self._sequence}"
            cache_key = f"cache:{subject.subject_id}:{self._sequence}"
            self._validate_payload(payload)
            self._cache.put(cache_key, payload.payload)
            descriptors.append(
                EvidenceDescriptor(
                    evidence_id=evidence_id,
                    subject_id=subject.subject_id,
                    evidence_type=payload.evidence_type,
                    artifact_type=payload.artifact_type,
                    source_identity=payload.source_identity,
                    coverage_start=payload.coverage_start,
                    coverage_end=payload.coverage_end,
                    row_count=payload.row_count,
                    schema=payload.schema,
                    cache_key=cache_key,
                    provenance=dict(payload.provenance),
                    neutral_semantics=payload.neutral_semantics,
                )
            )
        return tuple(descriptors)

    @staticmethod
    def _validate_payload(payload: IntakePayload) -> None:
        if not payload.evidence_type.strip():
            raise ValueError("evidence_type cannot be blank")
        if not payload.artifact_type.strip():
            raise ValueError("artifact_type cannot be blank")
        if not payload.source_identity.strip():
            raise ValueError("source_identity cannot be blank")
        if payload.row_count is not None and payload.row_count < 0:
            raise ValueError("row_count cannot be negative")
        if len(set(payload.schema)) != len(payload.schema):
            raise ValueError("schema contains duplicate field names")
