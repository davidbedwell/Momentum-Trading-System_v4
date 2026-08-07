from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterable, Mapping

from Core.research_nexus.models import ArtifactReference
from Core.research_nexus.storage.ports import IndexDocument


class IndexStoreError(RuntimeError):
    """Base class for SQLite index-store failures."""


class UnsupportedIndexCriterionError(IndexStoreError):
    """Raised when a search criterion cannot be represented by this backend."""


class SQLiteIndexStore:
    """SQLite implementation of the IndexStore port.

    This is a replaceable retrieval/discovery index, not the canonical artifact
    catalog. It stores backend-neutral IndexDocument fields as canonical JSON
    and returns governed ArtifactReference values only.
    """

    _SCHEMA_VERSION = 1

    def __init__(self, database_path: Path) -> None:
        self._database_path = Path(database_path).expanduser().resolve()
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def upsert(self, document: IndexDocument) -> None:
        fields_json = self._canonical_json(document.fields)

        with self._transaction() as conn:
            conn.execute(
                """
                INSERT INTO index_documents (
                    artifact_id,
                    artifact_version,
                    fields_json
                ) VALUES (?, ?, ?)
                ON CONFLICT (artifact_id, artifact_version)
                DO UPDATE SET fields_json = excluded.fields_json
                """,
                (
                    document.artifact_ref.artifact_id,
                    document.artifact_ref.artifact_version,
                    fields_json,
                ),
            )

    def remove(self, artifact_ref: ArtifactReference) -> None:
        with self._transaction() as conn:
            conn.execute(
                """
                DELETE FROM index_documents
                WHERE artifact_id = ? AND artifact_version = ?
                """,
                (
                    artifact_ref.artifact_id,
                    artifact_ref.artifact_version,
                ),
            )

    def search(
        self,
        criteria: Mapping[str, Any],
        *,
        limit: int | None = None,
    ) -> tuple[ArtifactReference, ...]:
        if limit is not None and limit < 0:
            raise ValueError("limit must be non-negative or None")
        if limit == 0:
            return ()

        self._validate_criteria(criteria)

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT artifact_id, artifact_version, fields_json
                FROM index_documents
                ORDER BY artifact_id ASC, artifact_version ASC
                """
            ).fetchall()

        matches: list[ArtifactReference] = []

        for row in rows:
            fields = json.loads(row["fields_json"])
            if self._matches(fields, criteria):
                matches.append(
                    ArtifactReference(
                        row["artifact_id"],
                        row["artifact_version"],
                    )
                )
                if limit is not None and len(matches) >= limit:
                    break

        return tuple(matches)

    def _initialize(self) -> None:
        with self._connect() as conn:
            current = conn.execute("PRAGMA user_version").fetchone()[0]

            if current > self._SCHEMA_VERSION:
                raise IndexStoreError(
                    f"Index schema version {current} is newer than supported "
                    f"version {self._SCHEMA_VERSION}"
                )

            if current < 1:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS index_schema_migrations (
                        version INTEGER PRIMARY KEY
                    );

                    CREATE TABLE IF NOT EXISTS index_documents (
                        artifact_id TEXT NOT NULL,
                        artifact_version INTEGER NOT NULL,
                        fields_json TEXT NOT NULL,
                        PRIMARY KEY (artifact_id, artifact_version)
                    );

                    CREATE INDEX IF NOT EXISTS idx_index_documents_artifact_id
                        ON index_documents (artifact_id);
                    """
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO index_schema_migrations (version)
                    VALUES (1)
                    """
                )
                conn.execute("PRAGMA user_version = 1")
                conn.commit()

    @classmethod
    def _validate_criteria(cls, criteria: Mapping[str, Any]) -> None:
        if not isinstance(criteria, Mapping):
            raise TypeError("criteria must be a mapping")

        for key, expected in criteria.items():
            if not isinstance(key, str) or not key:
                raise UnsupportedIndexCriterionError(
                    "criterion keys must be non-empty strings"
                )
            cls._validate_value(expected)

    @classmethod
    def _validate_value(cls, value: Any) -> None:
        if value is None or isinstance(value, (str, int, float, bool)):
            return

        if isinstance(value, (list, tuple)):
            for item in value:
                cls._validate_value(item)
            return

        raise UnsupportedIndexCriterionError(
            f"unsupported criterion value type: {type(value).__name__}"
        )

    @classmethod
    def _matches(
        cls,
        fields: Mapping[str, Any],
        criteria: Mapping[str, Any],
    ) -> bool:
        for key, expected in criteria.items():
            if key not in fields:
                return False
            if not cls._value_matches(fields[key], expected):
                return False
        return True

    @classmethod
    def _value_matches(cls, actual: Any, expected: Any) -> bool:
        if isinstance(actual, list):
            if isinstance(expected, (list, tuple)):
                return all(item in actual for item in expected)
            return expected in actual

        if isinstance(expected, (list, tuple)):
            return actual in expected

        return actual == expected

    @staticmethod
    def _canonical_json(value: Mapping[str, Any]) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @contextmanager
    def _connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    @contextmanager
    def _transaction(self) -> Iterable[sqlite3.Connection]:
        with self._connect() as conn:
            try:
                conn.execute("BEGIN IMMEDIATE")
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
