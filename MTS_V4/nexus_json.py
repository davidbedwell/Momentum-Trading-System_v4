from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .contracts import Finding, SubjectMetadata
from .nexus import NexusError


class JsonResearchNexus:
    """Small durable v4 Nexus reference implementation.

    The on-disk document contains only subject metadata and significant findings.
    There is no raw-evidence payload field and no dataset publication API.
    """

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._subjects: dict[str, SubjectMetadata] = {}
        self._findings: dict[str, Finding] = {}
        self._load()

    def upsert_subject(self, metadata: SubjectMetadata) -> None:
        if not metadata.subject_id:
            raise NexusError("subject_id cannot be blank")
        self._subjects[metadata.subject_id] = metadata
        self._flush()

    def publish_finding(self, finding: Finding) -> None:
        if finding.subject_id not in self._subjects:
            raise NexusError(f"Cannot publish finding for unknown subject: {finding.subject_id}")
        existing = self._findings.get(finding.finding_id)
        if existing is not None and existing != finding:
            raise NexusError(f"finding_id already exists with different content: {finding.finding_id}")
        self._findings[finding.finding_id] = finding
        self._flush()

    def get_subject(self, subject_id: str) -> SubjectMetadata | None:
        return self._subjects.get(subject_id)

    def get_finding(self, finding_id: str) -> Finding | None:
        return self._findings.get(finding_id)

    def findings_for_subject(self, subject_id: str) -> tuple[Finding, ...]:
        return tuple(
            finding
            for _, finding in sorted(self._findings.items())
            if finding.subject_id == subject_id
        )

    def _load(self) -> None:
        if not self._path.exists():
            return
        document = json.loads(self._path.read_text(encoding="utf-8"))
        for raw in document.get("subjects", []):
            metadata = SubjectMetadata(**raw)
            self._subjects[metadata.subject_id] = metadata
        for raw in document.get("findings", []):
            raw = dict(raw)
            raw["supporting_result_ids"] = tuple(raw.get("supporting_result_ids", ()))
            raw["evidence_ids"] = tuple(raw.get("evidence_ids", ()))
            raw["limitations"] = tuple(raw.get("limitations", ()))
            raw["relationships"] = tuple(raw.get("relationships", ()))
            finding = Finding(**raw)
            self._findings[finding.finding_id] = finding

    def _flush(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        document = {
            "format": "MTS_V4_RESEARCH_NEXUS_V1",
            "subjects": [asdict(self._subjects[key]) for key in sorted(self._subjects)],
            "findings": [asdict(self._findings[key]) for key in sorted(self._findings)],
        }
        temporary = self._path.with_suffix(self._path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(document, indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        temporary.replace(self._path)
