from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from Core.research_nexus import (
    ArtifactNotFoundError,
    ArtifactReference,
    Producer,
    Provenance,
    ResearchNexus,
    SchemaValidator,
    create_artifact_envelope,
)

from .canonical import canonical_json_bytes
from .models import AnalysisEvidence, AnalysisFinding


PRODUCER_ID = "analysis-engine-v2"


@dataclass(frozen=True, slots=True)
class AnalysisPublication:
    artifact_ref: ArtifactReference
    reconciled: bool


class AnalysisNexusPublisher:
    """Publish validated Analysis Evidence/Finding through the public Nexus only."""

    def __init__(
        self,
        nexus: ResearchNexus,
        *,
        validator: SchemaValidator | None = None,
    ) -> None:
        self.nexus = nexus
        self.validator = validator or SchemaValidator()

    @staticmethod
    def _artifact_id(kind: str, semantic_fingerprint: str) -> str:
        digest = hashlib.sha256(
            f"mts.analysis|{kind}|{semantic_fingerprint}".encode("utf-8")
        ).hexdigest()
        return f"artifact:{digest[:32]}"

    def _canonical_created_at(
        self,
        ref: ArtifactReference,
        requested: datetime,
    ) -> datetime:
        try:
            existing = self.nexus.get(ref)
        except ArtifactNotFoundError:
            return requested.astimezone(timezone.utc)
        return existing.envelope.created_at

    def _publish(
        self,
        *,
        payload: Mapping[str, Any],
        semantic_fingerprint: str,
        artifact_type: str,
        schema_id: str,
        method_id: str,
        method_version: str,
        created_at: datetime,
        tags: tuple[str, ...] = (),
        parameters: Mapping[str, Any] | None = None,
    ) -> AnalysisPublication:
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")

        self.validator.validate(payload, schema_id=schema_id, schema_version=1)
        payload_bytes = canonical_json_bytes(payload)

        artifact_id = self._artifact_id(artifact_type, semantic_fingerprint)
        ref = ArtifactReference(artifact_id, 1)
        canonical_created_at = self._canonical_created_at(ref, created_at)

        envelope = create_artifact_envelope(
            artifact_type=artifact_type,
            schema_id=schema_id,
            schema_version=1,
            producer=Producer(
                producer_type="ENGINE",
                producer_id=PRODUCER_ID,
            ),
            provenance=Provenance(
                software_version="analysis-v2",
                method_id=method_id,
                parameters={
                    "method_version": method_version,
                    "semantic_fingerprint": semantic_fingerprint,
                    **dict(parameters or {}),
                },
            ),
            lifecycle_state="DRAFT",
            persistence_class="CLASS_II",
            retention_class="SEMI_PERMANENT",
            backup_requirement="REQUIRED",
            tags=tags,
            artifact_id=artifact_id,
            artifact_version=1,
            created_at=canonical_created_at,
        )
        result = self.nexus.publish(
            envelope=envelope,
            payload=payload_bytes,
            media_type="application/json",
            index_fields={
                "artifact_type": artifact_type,
                "schema_id": schema_id,
                "producer_id": PRODUCER_ID,
                "tags": list(tags),
            },
        )
        return AnalysisPublication(
            artifact_ref=result.artifact_ref,
            reconciled=bool(result.reconciled),
        )

    def publish_evidence(
        self,
        evidence: AnalysisEvidence,
        *,
        created_at: datetime,
        tags: tuple[str, ...] = (),
    ) -> AnalysisPublication:
        return self._publish(
            payload=evidence.to_payload(),
            semantic_fingerprint=evidence.semantic_fingerprint,
            artifact_type="EVIDENCE",
            schema_id="mts.analysis-evidence",
            method_id=evidence.method_id,
            method_version=evidence.method_version,
            created_at=created_at,
            tags=tags,
            parameters={
                "task_id": evidence.task_id,
                "context_fingerprint": evidence.context_fingerprint,
            },
        )

    def publish_finding(
        self,
        finding: AnalysisFinding,
        *,
        created_at: datetime,
        tags: tuple[str, ...] = (),
    ) -> AnalysisPublication:
        return self._publish(
            payload=finding.to_payload(),
            semantic_fingerprint=finding.semantic_fingerprint,
            artifact_type="FINDING",
            schema_id="mts.analysis-finding",
            method_id=finding.method_id,
            method_version=finding.method_version,
            created_at=created_at,
            tags=tags,
            parameters={
                "task_id": finding.task_id,
                "research_mode": finding.research_mode.value,
            },
        )
