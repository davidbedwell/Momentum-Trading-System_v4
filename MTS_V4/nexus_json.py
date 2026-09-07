from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .contracts import (
    AnalysisResultMetadata,
    EvidenceMetadata,
    Finding,
    FindingRetraction,
    SubjectMetadata,
)
from .nexus import NexusError


class JsonResearchNexus:
    """Small durable v4 Nexus reference implementation.

    The on-disk document contains ticker/subject metadata, immutable evidence and
    Analysis-result lineage metadata, and significant RD findings. It contains no
    raw evidence payload, temporary cache key, or reusable Analysis result payload.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._subjects: dict[str, SubjectMetadata] = {}
        self._evidence_metadata: dict[str, EvidenceMetadata] = {}
        self._analysis_result_metadata: dict[str, AnalysisResultMetadata] = {}
        self._findings: dict[str, Finding] = {}
        self._finding_retractions: dict[str, FindingRetraction] = {}
        self._load()

    def upsert_subject(self, metadata: SubjectMetadata) -> None:
        if not metadata.subject_id:
            raise NexusError("subject_id cannot be blank")
        self._subjects[metadata.subject_id] = metadata
        self._flush()

    def upsert_evidence_metadata(self, metadata: EvidenceMetadata) -> None:
        if metadata.subject_id not in self._subjects:
            raise NexusError(
                f"Cannot persist evidence metadata for unknown subject: {metadata.subject_id}"
            )
        existing = self._evidence_metadata.get(metadata.evidence_id)
        if existing is not None and existing != metadata:
            raise NexusError(
                f"evidence_id already exists with different metadata: {metadata.evidence_id}"
            )
        self._evidence_metadata[metadata.evidence_id] = metadata
        self._flush()

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
        self._flush()

    def publish_finding(self, finding: Finding) -> None:
        if finding.subject_id not in self._subjects:
            raise NexusError(f"Cannot publish finding for unknown subject: {finding.subject_id}")
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
        self._flush()

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
        self._flush()
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

    def _load(self) -> None:
        if not self._path.exists():
            return
        document = json.loads(self._path.read_text(encoding="utf-8"))
        for raw in document.get("subjects", []):
            metadata = SubjectMetadata(**raw)
            self._subjects[metadata.subject_id] = metadata
        for raw in document.get("evidence_metadata", []):
            raw = dict(raw)
            raw["schema"] = tuple(raw.get("schema", ()))
            metadata = EvidenceMetadata(**raw)
            self._evidence_metadata[metadata.evidence_id] = metadata
        for raw in document.get("analysis_result_metadata", []):
            raw = dict(raw)
            raw["evidence_ids"] = tuple(raw.get("evidence_ids", ()))
            metadata = AnalysisResultMetadata(**raw)
            self._analysis_result_metadata[metadata.result_id] = metadata
        for raw in document.get("findings", []):
            raw = dict(raw)
            raw["supporting_result_ids"] = tuple(raw.get("supporting_result_ids", ()))
            raw["evidence_ids"] = tuple(raw.get("evidence_ids", ()))
            metadata = dict(raw.get("metadata", {}))
            for legacy_name in (
                "significance",
                "status",
                "applicability",
                "limitations",
                "relationships",
            ):
                if legacy_name in raw:
                    metadata.setdefault(legacy_name, raw.pop(legacy_name))
            raw["metadata"] = metadata
            finding = Finding(**raw)
            self._findings[finding.finding_id] = finding
        for raw in document.get("finding_retractions", []):
            retraction = FindingRetraction(**raw)
            if retraction.finding_id in self._findings:
                self._finding_retractions[retraction.finding_id] = retraction

    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "format": "MTS_V4_RESEARCH_NEXUS_V1",
            "subjects": [asdict(self._subjects[key]) for key in sorted(self._subjects)],
            "evidence_metadata": [
                asdict(self._evidence_metadata[key]) for key in sorted(self._evidence_metadata)
            ],
            "analysis_result_metadata": [
                asdict(self._analysis_result_metadata[key])
                for key in sorted(self._analysis_result_metadata)
            ],
            "findings": [asdict(self._findings[key]) for key in sorted(self._findings)],
            "finding_retractions": [
                asdict(self._finding_retractions[key])
                for key in sorted(self._finding_retractions)
            ],
        }
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self._path)
