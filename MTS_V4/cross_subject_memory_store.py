from __future__ import annotations

from dataclasses import dataclass
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

from .cross_subject_memory import (
    InMemoryCrossSubjectScientificMemory,
    ResearchFrontierState,
    ScientificMemoryRecord,
)


@dataclass(frozen=True, slots=True)
class CrossSubjectMemorySnapshotSelection:
    """Objective selection of one current accumulated scientific-memory snapshot."""

    source_path: Path
    store: "JsonCrossSubjectScientificMemoryStore"
    superseded_paths: tuple[Path, ...] = ()


class JsonCrossSubjectScientificMemoryStore(InMemoryCrossSubjectScientificMemory):
    """Durable compact cross-subject scientific memory; never stores raw rows."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str | Path) -> None:
        super().__init__()
        self._path = Path(path)
        self._load()

    @property
    def path(self) -> Path:
        return self._path

    def publish(self, record: ScientificMemoryRecord) -> None:
        self.publish_batch((record,))

    def publish_batch(self, records: Sequence[ScientificMemoryRecord]) -> None:
        super().publish_batch(records)
        self._persist()

    def set_frontier(self, frontier: ResearchFrontierState) -> None:
        super().set_frontier(frontier)
        self._persist()

    @staticmethod
    def _record_map(store: "JsonCrossSubjectScientificMemoryStore") -> dict[str, ScientificMemoryRecord]:
        return {record.record_id: record for record in store.records()}

    @staticmethod
    def _frontier_version(store: "JsonCrossSubjectScientificMemoryStore") -> int:
        frontier = store.frontier()
        return frontier.version if frontier is not None else 0

    @classmethod
    def _supersedes(
        cls,
        candidate: "JsonCrossSubjectScientificMemoryStore",
        prior: "JsonCrossSubjectScientificMemoryStore",
    ) -> bool:
        """Return True only for objective accumulated-snapshot containment.

        Supersession is storage/provenance semantics, not scientific ranking. Every
        prior record must exist byte-for-object identically in the candidate and
        the candidate may not regress the RD-authored frontier version.
        """
        candidate_records = cls._record_map(candidate)
        prior_records = cls._record_map(prior)
        if not prior_records.keys() <= candidate_records.keys():
            return False
        if any(candidate_records[key] != record for key, record in prior_records.items()):
            return False
        return cls._frontier_version(candidate) >= cls._frontier_version(prior)

    @classmethod
    def discover_current(
        cls,
        root: str | Path,
        *,
        pattern: str = "mts-v4-*/**/cross_subject_memory.json",
    ) -> CrossSubjectMemorySnapshotSelection | None:
        """Find the unique current accumulated snapshot under ``root``.

        Historical snapshots remain on disk for provenance. A snapshot is excluded
        from runtime scientific context only when another snapshot objectively
        contains all of its records with identical content and has an equal-or-newer
        frontier version. If multiple incomparable current snapshots remain, fail
        closed rather than letting deterministic code choose scientific authority.
        """
        root_path = Path(root)
        loaded: list[tuple[Path, JsonCrossSubjectScientificMemoryStore]] = []
        seen_documents: set[str] = set()

        for path in sorted(root_path.glob(pattern)):
            try:
                raw = json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(raw, Mapping):
                continue
            fingerprint = json.dumps(raw, sort_keys=True, default=str, separators=(",", ":"))
            if fingerprint in seen_documents:
                continue
            seen_documents.add(fingerprint)
            try:
                loaded.append((path, cls(path)))
            except (KeyError, TypeError, ValueError):
                continue

        if not loaded:
            return None

        # A reused durable record identity with divergent content is an objective
        # provenance conflict. Refuse to hide it by snapshot selection.
        canonical_records: dict[str, ScientificMemoryRecord] = {}
        for path, store in loaded:
            for record in store.records():
                existing = canonical_records.get(record.record_id)
                if existing is not None and existing != record:
                    raise ValueError(
                        "conflicting cross-subject scientific memory record_id across snapshots: "
                        f"{record.record_id} (including {path})"
                    )
                canonical_records[record.record_id] = record

        maximal: list[tuple[Path, JsonCrossSubjectScientificMemoryStore]] = []
        superseded_paths: set[Path] = set()
        for index, (path, store) in enumerate(loaded):
            superseded = False
            for other_index, (other_path, other_store) in enumerate(loaded):
                if index == other_index:
                    continue
                if cls._supersedes(other_store, store):
                    same_records = cls._record_map(other_store) == cls._record_map(store)
                    same_frontier = cls._frontier_version(other_store) == cls._frontier_version(store)
                    # Exact semantic equivalents were already document-deduped when
                    # byte-identical. If metadata formatting differs but scientific
                    # state is identical, either path is equivalent; select the
                    # lexically later path deterministically as provenance only.
                    if same_records and same_frontier:
                        if str(other_path) > str(path):
                            superseded = True
                            superseded_paths.add(path)
                            break
                        continue
                    superseded = True
                    superseded_paths.add(path)
                    break
            if not superseded:
                maximal.append((path, store))

        if len(maximal) != 1:
            paths = ", ".join(str(path) for path, _ in maximal)
            raise ValueError(
                "cross-subject scientific memory has multiple incomparable current snapshots; "
                f"AI/RD reconciliation is required before runtime consumption: {paths}"
            )

        current_path, current_store = maximal[0]
        return CrossSubjectMemorySnapshotSelection(
            source_path=current_path,
            store=current_store,
            superseded_paths=tuple(sorted(superseded_paths, key=str)),
        )

    def _load(self) -> None:
        if not self._path.exists():
            return
        document = json.loads(self._path.read_text(encoding="utf-8"))
        raw_records = document.get("records", [])
        if not isinstance(raw_records, list):
            raise ValueError("cross-subject memory records must be an array")
        loaded_records: list[ScientificMemoryRecord] = []
        for item in raw_records:
            if not isinstance(item, Mapping):
                raise ValueError("cross-subject memory record must be an object")
            loaded_records.append(
                ScientificMemoryRecord(
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
            )
        super().publish_batch(loaded_records)

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
        records = self.records()
        return {
            "schema_version": self.SCHEMA_VERSION,
            "policy": {
                "contains_raw_rows": False,
                "contains_reusable_analysis_payloads": False,
                "scientific_content_authority": "AI_RD",
            },
            "snapshot": {
                "record_count": len(records),
                "record_ids": [record.record_id for record in records],
                "frontier_version": frontier.version if frontier is not None else 0,
                "supersession_semantics": "OBJECTIVE_ACCUMULATED_RECORD_CONTAINMENT",
            },
            "records": [record.compact_context() for record in records],
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
