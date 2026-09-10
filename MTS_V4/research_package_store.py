from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from .research_package import (
    ResearchAnalysisRecord,
    ResearchPackage,
    ResearchPackageError,
    ResearchPackageStateTransition,
    ResearchQuestionRecord,
)


class JsonResearchPackageStore:
    """Durable one-object-per-RP store.

    A later RP is always written to a distinct file keyed by its stable rp_id.
    Updating an OPEN RP rewrites only that RP's accumulated representation.
    CLOSED RPs are immutable.
    """

    FORMAT = "MTS_V4_RESEARCH_PACKAGE_V1"

    def __init__(self, directory: str | Path) -> None:
        self._directory = Path(directory)

    @staticmethod
    def _safe_name(rp_id: str) -> str:
        if not rp_id or any(part in rp_id for part in ("/", "\\", "..")):
            raise ResearchPackageError(f"invalid rp_id for durable storage: {rp_id!r}")
        return rp_id

    def _path(self, rp_id: str) -> Path:
        return self._directory / f"{self._safe_name(rp_id)}.json"

    def create(self, package: ResearchPackage) -> None:
        path = self._path(package.rp_id)
        if path.exists():
            raise ResearchPackageError(f"research package already exists: {package.rp_id}")
        if package.parent_rp_id is not None:
            parent = self.load(package.parent_rp_id)
            if parent is None:
                raise ResearchPackageError(
                    f"missing parent_rp_id: {package.parent_rp_id}"
                )
            if parent.subject_id != package.subject_id:
                raise ResearchPackageError(
                    "parent and child research packages must share subject_id"
                )
        self._write_new(path, package)

    def save(self, package: ResearchPackage) -> None:
        path = self._path(package.rp_id)
        current = self.load(package.rp_id)
        if current is None:
            raise ResearchPackageError(f"research package does not exist: {package.rp_id}")
        if current.status == "CLOSED":
            raise ResearchPackageError(
                f"closed research package is immutable: {package.rp_id}"
            )
        if package.version <= current.version:
            raise ResearchPackageError(
                f"research package version must advance: {package.rp_id}"
            )
        if (
            package.rp_id != current.rp_id
            or package.subject_id != current.subject_id
            or package.campaign_id != current.campaign_id
            or package.parent_rp_id != current.parent_rp_id
            or package.originating_question != current.originating_question
            or package.originating_rationale != current.originating_rationale
            or package.created_by != current.created_by
            or package.created_at != current.created_at
        ):
            raise ResearchPackageError(
                f"research package immutable identity fields changed: {package.rp_id}"
            )
        self._write_replace(path, package)

    def load(self, rp_id: str) -> ResearchPackage | None:
        path = self._path(rp_id)
        if not path.exists():
            return None
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("format") != self.FORMAT:
            raise ResearchPackageError(f"unsupported research package format: {rp_id}")
        return self._decode(raw["research_package"])

    def list_ids(self) -> tuple[str, ...]:
        if not self._directory.exists():
            return ()
        result: list[str] = []
        for path in sorted(self._directory.glob("*.json")):
            raw = json.loads(path.read_text(encoding="utf-8"))
            if raw.get("format") == self.FORMAT:
                result.append(str(raw["research_package"]["rp_id"]))
        return tuple(result)

    def _document(self, package: ResearchPackage) -> str:
        document = {
            "format": self.FORMAT,
            "research_package": asdict(package),
        }
        serialized = json.dumps(document, indent=2, sort_keys=True, default=str) + "\n"
        forbidden = ('"payload"', '"rows"', '"cache_key"')
        if any(token in serialized for token in forbidden):
            raise ResearchPackageError(
                "research package attempted to persist raw/cache evidence data"
            )
        return serialized

    def _write_new(self, path: Path, package: ResearchPackage) -> None:
        self._directory.mkdir(parents=True, exist_ok=True)
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(self._document(package))
        except FileExistsError as exc:
            raise ResearchPackageError(
                f"research package already exists: {package.rp_id}"
            ) from exc

    def _write_replace(self, path: Path, package: ResearchPackage) -> None:
        serialized = self._document(package)
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(serialized, encoding="utf-8")
        temporary.replace(path)

    @staticmethod
    def _decode(raw: Mapping[str, Any]) -> ResearchPackage:
        questions = tuple(
            ResearchQuestionRecord(**item) for item in raw.get("questions", ())
        )
        analyses = tuple(
            ResearchAnalysisRecord(
                **{
                    **item,
                    "evidence_ids": tuple(item.get("evidence_ids", ())),
                    "analysis_inputs": tuple(item.get("analysis_inputs", ())),
                }
            )
            for item in raw.get("analyses", ())
        )
        transitions = tuple(
            ResearchPackageStateTransition(**item)
            for item in raw.get("state_transitions", ())
        )
        return ResearchPackage(
            **{
                **raw,
                "hypotheses": tuple(raw.get("hypotheses", ())),
                "questions": questions,
                "analyses": analyses,
                "findings": tuple(raw.get("findings", ())),
                "unresolved_issues": tuple(raw.get("unresolved_issues", ())),
                "state_transitions": transitions,
            }
        )
