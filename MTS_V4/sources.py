from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .contracts import SubjectMetadata
from .intake import IntakePayload


class SourceAcquisitionError(RuntimeError):
    """Objective failure to acquire or represent a requested evidence source."""


@dataclass(frozen=True, slots=True)
class TabularSourceSpec:
    """Mechanical description of a tabular evidence source.

    Evidence meaning is supplied explicitly; the adapter does not infer market
    semantics, scientific relevance, column roles, or appropriate research use.
    """

    evidence_type: str
    artifact_type: str
    neutral_semantics: str
    source_identity: str
    time_column: str | None = None


class CsvFileSource:
    """Acquire a normalized row dataset from a local CSV file.

    The adapter records reproducibility metadata sufficient to compare a later
    acquisition without storing the reproducible dataset in Nexus.
    """

    def __init__(self, path: str | Path, spec: TabularSourceSpec) -> None:
        self._path = Path(path).expanduser()
        self._spec = spec

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        if not self._path.is_file():
            raise SourceAcquisitionError(f"source file does not exist: {self._path}")
        raw = self._path.read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise SourceAcquisitionError("CSV source is not UTF-8 text") from exc
        reader = csv.DictReader(text.splitlines())
        if reader.fieldnames is None:
            raise SourceAcquisitionError("CSV source has no header")
        rows = [dict(row) for row in reader]
        schema = tuple(str(name) for name in reader.fieldnames)
        coverage_start, coverage_end = _coverage(rows, self._spec.time_column)
        acquired_at = datetime.now(timezone.utc).isoformat()
        yield IntakePayload(
            payload=rows,
            evidence_type=self._spec.evidence_type,
            artifact_type=self._spec.artifact_type,
            source_identity=self._spec.source_identity,
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            row_count=len(rows),
            schema=schema,
            provenance={
                "adapter": "CsvFileSource",
                "path_name": self._path.name,
                "sha256": digest,
                "byte_count": len(raw),
                "acquired_at_utc": acquired_at,
                "subject_id": subject.subject_id,
            },
            neutral_semantics=self._spec.neutral_semantics,
        )


class JsonRowsFileSource:
    """Acquire a JSON array of row objects with the same neutral boundary."""

    def __init__(self, path: str | Path, spec: TabularSourceSpec) -> None:
        self._path = Path(path).expanduser()
        self._spec = spec

    def acquire(self, subject: SubjectMetadata) -> Iterable[IntakePayload]:
        if not self._path.is_file():
            raise SourceAcquisitionError(f"source file does not exist: {self._path}")
        raw = self._path.read_bytes()
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SourceAcquisitionError("JSON source is not valid UTF-8 JSON") from exc
        if not isinstance(document, list) or not all(isinstance(row, Mapping) for row in document):
            raise SourceAcquisitionError("JSON tabular source must be an array of row objects")
        rows = [dict(row) for row in document]
        schema = _schema(rows)
        coverage_start, coverage_end = _coverage(rows, self._spec.time_column)
        yield IntakePayload(
            payload=rows,
            evidence_type=self._spec.evidence_type,
            artifact_type=self._spec.artifact_type,
            source_identity=self._spec.source_identity,
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            row_count=len(rows),
            schema=schema,
            provenance={
                "adapter": "JsonRowsFileSource",
                "path_name": self._path.name,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "byte_count": len(raw),
                "acquired_at_utc": datetime.now(timezone.utc).isoformat(),
                "subject_id": subject.subject_id,
            },
            neutral_semantics=self._spec.neutral_semantics,
        )


def _schema(rows: Sequence[Mapping[str, Any]]) -> tuple[str, ...]:
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for key in row:
            name = str(key)
            if name not in seen:
                seen.add(name)
                names.append(name)
    return tuple(names)


def _coverage(rows: Sequence[Mapping[str, Any]], time_column: str | None) -> tuple[str | None, str | None]:
    if time_column is None:
        return None, None
    if not rows:
        return None, None
    if any(time_column not in row for row in rows):
        raise SourceAcquisitionError(f"declared time_column missing from one or more rows: {time_column}")
    values = [str(row[time_column]) for row in rows]
    return min(values), max(values)
