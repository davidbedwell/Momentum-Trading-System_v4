from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, Protocol

from .contracts import EvidenceMetadata, Finding, FindingRetraction, SubjectMetadata


class NexusError(RuntimeError):
    pass


class ResearchNexus(Protocol):
    def upsert_subject(self, metadata: SubjectMetadata) -> None: ...
    def upsert_evidence_metadata(self, metadata: EvidenceMetadata) -> None: ...
    def publish_finding(self, finding: Finding) -> None: ...
    def retract_finding(
        self,
        finding_id: str,
        *,
        reason: str,
        initiated_by: str,
        replacement_finding_id: str | None = None,
    ) -> FindingRetraction: ...
    def get_subject(self, subject_id: str) -> SubjectMetadata | None: ...
    def get_evidence_metadata(self, evidence_id: str) -> EvidenceMetadata | None: ...
    def evidence_metadata_for_subject(self, subject_id: str) -> tuple[EvidenceMetadata, ...]: ...
    def get_finding(self, finding_id: str) -> Finding | None: ...
    def findings_for_subject(self, subject_id: str) -> tuple[Finding, ...]: ...
    def get_finding_retraction(self, finding_id: str) -> FindingRetraction | None: ...


@dataclass(slots=True)
class InMemoryResearchNexus:
    """Reference durable-memory implementation for v4 tests.

    This API deliberately has no raw-dataset publication method. Evidence
    persistence is metadata-only and therefore cannot hold a campaign cache key
    or source payload.
    """

    _subjects: dict[str, SubjectMetadata] = field(default_factory=dict)
    _evidence_metadata: dict[str, EvidenceMetadata] = field(default_factory=dict)
    _findings: dict[str, Finding] = field(default_factory=dict)
    _finding_retractions: dict[str, FindingRetraction] = field(default_factory=dict)

    def upsert_subject(self, metadata: SubjectMetadata) -> None:
        if not metadata.subject_id:
            raise NexusError("subject_id cannot be blank")
        self._subjects[metadata.subject_id] = metadata

    def upsert_evidence_metadata(self, metadata: EvidenceMetadata) -> None:
        if metadata.subject_id not in self._subjects:
            raise NexusError(
                f"Cannot persist evidence metadata for unknown subject: {metadata.subject_id}"
            )
        self._evidence_metadata[metadata.evidence_id] = metadata

    def publish_finding(self, finding: Finding) -> None:
        if finding.subject_id not in self._subjects:
            raise NexusError(
                f"Cannot publish finding for unknown subject: {finding.subject_id}"
            )
        existing = self._findings.get(finding.finding_id)
        if existing is not None and existing != finding:
            raise NexusError(f"finding_id already exists with different content: {finding.finding_id}")
        if finding.finding_id in self._finding_retractions:
            raise NexusError(f"cannot republish retracted finding_id: {finding.finding_id}")
        self._findings[finding.finding_id] = finding

    def retract_finding(
        self,
        finding_id: str,
        *,
        reason: str,
        initiated_by: str,
        replacement_finding_id: str | None = None,
    ) -> FindingRetraction:
        if finding_id not in self._findings:
            raise NexusError(f"cannot retract unknown finding_id: {finding_id}")
        if not reason.strip():
            raise NexusError("retraction reason cannot be blank")
        if not initiated_by.strip():
            raise NexusError("retraction initiator cannot be blank")
        existing = self._finding_retractions.get(finding_id)
        if existing is not None:
            return existing
        retraction = FindingRetraction(
            finding_id=finding_id,
            reason=reason,
            initiated_by=initiated_by,
            retracted_at_utc=datetime.now(timezone.utc).isoformat(),
            replacement_finding_id=replacement_finding_id,
        )
        self._finding_retractions[finding_id] = retraction
        return retraction

    def get_subject(self, subject_id: str) -> SubjectMetadata | None:
        return self._subjects.get(subject_id)

    def get_evidence_metadata(self, evidence_id: str) -> EvidenceMetadata | None:
        return self._evidence_metadata.get(evidence_id)

    def evidence_metadata_for_subject(self, subject_id: str) -> tuple[EvidenceMetadata, ...]:
        return tuple(
            metadata
            for _, metadata in sorted(self._evidence_metadata.items())
            if metadata.subject_id == subject_id
        )

    def get_finding(self, finding_id: str) -> Finding | None:
        if finding_id in self._finding_retractions:
            return None
        return self._findings.get(finding_id)

    def findings_for_subject(self, subject_id: str) -> tuple[Finding, ...]:
        return tuple(
            finding
            for finding_id, finding in sorted(self._findings.items())
            if finding.subject_id == subject_id and finding_id not in self._finding_retractions
        )

    def get_finding_retraction(self, finding_id: str) -> FindingRetraction | None:
        return self._finding_retractions.get(finding_id)

    def snapshot_metadata(self) -> Mapping[str, int]:
        return {
            "subjects": len(self._subjects),
            "evidence_metadata": len(self._evidence_metadata),
            "findings": len(self._findings),
            "finding_retractions": len(self._finding_retractions),
            "active_findings": len(self._findings) - len(self._finding_retractions),
        }
