from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping

from .cross_subject_memory import (
    InMemoryCrossSubjectScientificMemory,
    ResearchFrontierState,
    ScientificMemoryRecord,
)


class JsonCrossSubjectScientificMemoryStore(InMemoryCrossSubjectScientificMemory):
    """Durable compact cross-subject scientific memory; never stores raw rows."""

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._load()

    def publish(self, record: ScientificMemoryRecord) -> None:
        super().publish(record)
        self._persist()

    def set_frontier(self, frontier: ResearchFrontierState) -> None:
        super().set_frontier(frontier)
        self._persist()

    def _load(self) -> None:
        if not self._path.exists():
            return
        document = json.loads(self._path.read_text(encoding="utf-8"))
        raw_records = document.get("records", [])
        if not isinstance(raw_records, list):
            raise ValueError("cross-subject memory records must be an array")
        for item in raw_records:
            if not isinstance(item, Mapping):
                raise ValueError("cross-subject memory record must be an object")
            record = ScientificMemoryRecord(
                record_id=str(item["record_id"]),
                subject_id=str(item["subject_id"]),
                kind=str(item["kind"]),
                summary=str(item["summary"]),
                rp_id=item.get("rp_id") if isinstance(item.get("rp_id"), str) else None,
                finding_id=item.get("finding_id") if isinstance(item.get("finding_id"), str) else None,
                hypothesis_id=item.get("hypothesis_id") if isinstance(item.get("hypothesis_id"), str) else None,
                result_ids=tuple(str(value) for value in item.get("result_ids", ())),
                evidence_ids=tuple(str(value) for value in item.get("evidence_ids", ())),
                status=item.get("status") if isinstance(item.get("status"), str) else None,
                metadata=dict(item.get("metadata", {})) if isinstance(item.get("metadata"), Mapping) else {},
            )
            super().publish(record)

        raw_frontier = document.get("frontier")
        if isinstance(raw_frontier, Mapping):
            frontier = ResearchFrontierState(
                version=int(raw_frontier["version"]),
                summary=str(raw_frontier["summary"]),
                open_questions=tuple(str(v) for v in raw_frontier.get("open_questions", ())),
                candidate_generalizations=tuple(str(v) for v in raw_frontier.get("candidate_generalizations", ())),
                contradictions=tuple(str(v) for v in raw_frontier.get("contradictions", ())),
                deprioritized_avenues=tuple(str(v) for v in raw_frontier.get("deprioritized_avenues", ())),
                missing_resources=tuple(str(v) for v in raw_frontier.get("missing_resources", ())),
                source_record_ids=tuple(str(v) for v in raw_frontier.get("source_record_ids", ())),
            )
            super().set_frontier(frontier)

    def _document(self) -> Mapping[str, Any]:
        frontier = self.frontier()
        return {
            "schema_version": 1,
            "policy": {
                "contains_raw_rows": False,
                "contains_reusable_analysis_payloads": False,
                "scientific_content_authority": "AI_RD",
            },
            "records": [record.compact_context() for record in self.records()],
            "frontier": frontier.compact_context() if frontier is not None else None,
        }

    def _persist(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(self._document(), sort_keys=True, indent=2, default=str) + "\n"
        fd, temporary_path = tempfile.mkstemp(
            prefix=self._path.name + ".",
            suffix=".tmp",
            dir=str(self._path.parent),
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_path, self._path)
        finally:
            if os.path.exists(temporary_path):
                os.unlink(temporary_path)
