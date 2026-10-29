from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping, Protocol

from .contracts import (
    AnalysisResultMetadata,
    EvidenceMetadata,
    Finding,
    FindingRetraction,
    SubjectMetadata,
)


class NexusError(RuntimeError):
    pass


class ResearchNexus(Protocol):
    def upsert_subject(self, metadata: SubjectMetadata) -> None: ...
    def upsert_evidence_metadata(self, metadata: EvidenceMetadata) -> None: ...
    def register_analysis_result_metadata(self, metadata: AnalysisResultMetadata) -> None: ...
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
    def get_analysis_result_metadata(self, result_id: str) -> AnalysisResultMetadata | None: ...
    def analysis_result_metadata_for_subject(self, subject_id: str) -> tuple[AnalysisResultMetadata, ...]: ...
    def get_finding(self, finding_id: str) -> Finding | None: ...
    def findings_for_subject(self, subject_id: str) -> tuple[Finding, ...]: ...
    def get_finding_retraction(self, finding_id: str) -> FindingRetraction | None: ...


@dataclass(slots=True)
class InMemoryResearchNexus:
    """Reference durable-memory implementation for v4 tests.

    The Nexus stores immutable identity/lineage metadata, never raw datasets or
    reusable result payloads. Reusing an existing evidence or result identity
    with different meaningful metadata is rejected so later acquisitions cannot
    silently rewrite the provenance of older findings. Acquisition-clock-only
    differences are accepted without replacing the first durable record.
    """

    _subjects: dict[str, SubjectMetadata] = field(default_factory=dict)
    _evidence_metadata: dict[str, EvidenceMetadata] = field(default_factory=dict)
    _analysis_result_metadata: dict[str, AnalysisResultMetadata] = field(default_factory=dict)
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
        existing = self._evidence_metadata.get(metadata.evidence_id)
        if existing is not None:
            if not existing.identity_equivalent(metadata):
                raise NexusError(
                    f"evidence_id already exists with different metadata: {metadata.evidence_id}"
                )
            return
        self._evidence_metadata[metadata.evidence_id] = metadata

    def register_analysis_result_metadata(self, metadata: AnalysisResultMetadata) -> None:
        if metadata.subject_id not in self._subjects:
            raise NexusError(
                f"Cannot persist result metadata for unknown subject: {metadata.subject_id}"
            )
        for evidence_id in metadata.evidence_ids:
            evidence = self._evidence_metadata.get(evidence_id)
            if evidence is None:
                raise NexusError(f"result cites unknown evidence_id: {evidence_id}")
            if evidence.subject_id != metadata.subject_id:
                raise NexusError(f"result/evidence subject lineage mismatch: {evidence_id}")
        existing = self._analysis_result_metadata.get(metadata.result_id)
        if existing is not None and existing != metadata:
            raise NexusError(
                f"result_id already exists with different metadata: {metadata.result_id}"
            )
        self._analysis_result_metadata[metadata.result_id] = metadata

    def publish_finding(self, finding: Finding) -> None:
        if finding.subject_id not in self._subjects:
            raise NexusError(
                f"Cannot publish finding for unknown subject: {finding.subject_id}"
            )
        cited_evidence = set(finding.evidence_ids)
        for evidence_id in finding.evidence_ids:
            evidence = self._evidence_metadata.get(evidence_id)
            if evidence is None:
                raise NexusError(f"finding cites unknown evidence_id: {evidence_id}")
            if evidence.subject_id != finding.subject_id:
                raise NexusError(f"finding/evidence subject lineage mismatch: {evidence_id}")
        for result_id in finding.supporting_result_ids:
            result = self._analysis_result_metadata.get(result_id)
            if result is None:
                raise NexusError(f"finding cites unknown result_id: {result_id}")
            if result.subject_id != finding.subject_id:
                raise NexusError(f"finding/result subject lineage mismatch: {result_id}")
            missing_lineage = set(result.evidence_ids) - cited_evidence
            if missing_lineage:
                raise NexusError(
                    "finding omits evidence lineage from supporting result "
                    f"{result_id}: {sorted(missing_lineage)}"
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

    def get_analysis_result_metadata(self, result_id: str) -> AnalysisResultMetadata | None:
        return self._analysis_result_metadata.get(result_id)

    def analysis_result_metadata_for_subject(self, subject_id: str) -> tuple[AnalysisResultMetadata, ...]:
        return tuple(
            metadata
            for _, metadata in sorted(self._analysis_result_metadata.items())
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
            "analysis_result_metadata": len(self._analysis_result_metadata),
            "findings": len(self._findings),
            "finding_retractions": len(self._finding_retractions),
            "active_findings": len(self._findings) - len(self._finding_retractions),
        }
