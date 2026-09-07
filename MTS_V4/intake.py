from __future__ import annotations

import hashlib
import json
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

    Intake does not decide scientific relevance or meaning. Evidence identities
    are content/source-derived so a later acquisition cannot silently overwrite
    durable metadata referenced by an older finding.
    """

    _ACQUISITION_ONLY_PROVENANCE_KEYS = frozenset(
        {
            "acquired_at",
            "acquired_at_utc",
            "fetched_at",
            "fetched_at_utc",
            "pulled_at",
            "pulled_at_utc",
            "requested_at",
            "requested_at_utc",
            "retrieved_at",
            "retrieved_at_utc",
        }
    )

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
            self._validate_payload(payload)
            content_identity = self._content_identity(payload.payload)
            evidence_id = self._evidence_identity(
                subject=subject,
                payload=payload,
                content_identity=content_identity,
            )
            cache_key = f"cache:{subject.subject_id}:{self._sequence}:{content_identity[:12]}"
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
                    content_identity=content_identity,
                )
            )
        return tuple(descriptors)

    @classmethod
    def _evidence_identity(
        cls,
        *,
        subject: SubjectMetadata,
        payload: IntakePayload,
        content_identity: str,
    ) -> str:
        identity_document = {
            "subject_id": subject.subject_id,
            "evidence_type": payload.evidence_type,
            "artifact_type": payload.artifact_type,
            "source_identity": payload.source_identity,
            "coverage_start": payload.coverage_start,
            "coverage_end": payload.coverage_end,
            "row_count": payload.row_count,
            "schema": list(payload.schema),
            "provenance": cls.meaningful_provenance(payload.provenance),
            "neutral_semantics": payload.neutral_semantics,
            "content_identity": content_identity,
        }
        digest = hashlib.sha256(
            json.dumps(identity_document, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        return f"evidence:{subject.subject_id}:{digest[:24]}"

    @staticmethod
    def _content_identity(payload: object) -> str:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()

    @classmethod
    def meaningful_provenance(cls, provenance: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            str(key): value
            for key, value in provenance.items()
            if str(key).lower() not in cls._ACQUISITION_ONLY_PROVENANCE_KEYS
        }

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
