from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from Core.research_nexus.models import (
    ArtifactEnvelope,
    ArtifactReference,
    Producer,
    Provenance,
)
from Core.research_nexus.storage.ports import (
    PublicationRecord,
    RelationshipRecord,
    RepresentationRecord,
)

_MIGRATION_VERSION = 1


class CatalogStoreError(RuntimeError):
    """Base class for SQLite catalog failures."""


class CatalogConflictError(CatalogStoreError):
    """Raised when immutable catalog state conflicts with an existing record."""


class RelationshipQueryError(CatalogStoreError):
    """Raised for unsupported relationship-query semantics."""


class SQLiteCatalogStore:
    """SQLite implementation of the CatalogStore port.

    SQLite row identity is never exposed. Canonical identity remains
    (artifact_id, artifact_version).
    """

    def __init__(self, database_path: Path) -> None:
        self._database_path = Path(database_path).expanduser().resolve()
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @property
    def database_path(self) -> Path:
        return self._database_path

    def get_artifact(
        self,
        artifact_ref: ArtifactReference,
    ) -> ArtifactEnvelope | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT artifact_id, artifact_version, artifact_type,
                       schema_id, schema_version, created_at,
                       producer_json, provenance_json, lifecycle_state,
                       persistence_class, retention_class,
                       backup_requirement, tags_json
                FROM artifacts
                WHERE artifact_id = ? AND artifact_version = ?
                """,
                (artifact_ref.artifact_id, artifact_ref.artifact_version),
            ).fetchone()

        if row is None:
            return None

        return self._envelope_from_row(row)

    def register_artifact(
        self,
        envelope: ArtifactEnvelope,
        representation: RepresentationRecord,
        relationships: Sequence[RelationshipRecord] = (),
        publication: PublicationRecord | None = None,
    ) -> None:
        if representation.artifact_ref != envelope.reference():
            raise CatalogStoreError(
                "Representation artifact reference does not match envelope identity"
            )

        if publication is not None and publication.artifact_ref != envelope.reference():
            raise CatalogStoreError(
                "Publication artifact reference does not match envelope identity"
            )

        with self._transaction() as conn:
            self._insert_or_reconcile_artifact(conn, envelope)
            self._insert_or_reconcile_representation(conn, representation)

            for relationship in relationships:
                self._insert_or_reconcile_relationship(conn, relationship)

            if publication is not None:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO publication_records (
                        artifact_id, artifact_version,
                        publication_state, recorded_at
                    ) VALUES (?, ?, ?, ?)
                    """,
                    (
                        publication.artifact_ref.artifact_id,
                        publication.artifact_ref.artifact_version,
                        publication.publication_state,
                        publication.recorded_at,
                    ),
                )

    def artifact_exists(self, artifact_ref: ArtifactReference) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM artifacts
                WHERE artifact_id = ? AND artifact_version = ?
                """,
                (artifact_ref.artifact_id, artifact_ref.artifact_version),
            ).fetchone()

        return row is not None

    def get_representation(
        self,
        artifact_ref: ArtifactReference,
    ) -> RepresentationRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT locator, media_type, content_hash,
                       size_bytes, created_at, verification_state
                FROM representations
                WHERE artifact_id = ? AND artifact_version = ?
                ORDER BY created_at ASC, locator ASC
                LIMIT 1
                """,
                (artifact_ref.artifact_id, artifact_ref.artifact_version),
            ).fetchone()

        if row is None:
            return None

        return RepresentationRecord(
            artifact_ref=artifact_ref,
            locator=row["locator"],
            media_type=row["media_type"],
            content_hash=row["content_hash"],
            size_bytes=row["size_bytes"],
            created_at=row["created_at"],
            verification_state=row["verification_state"],
        )

    def add_relationship(self, relationship: RelationshipRecord) -> None:
        with self._transaction() as conn:
            self._insert_or_reconcile_relationship(conn, relationship)

    def get_relationships(
        self,
        ref: Mapping[str, Any],
        *,
        direction: str = "BOTH",
        relationship_types: Sequence[str] = (),
    ) -> tuple[RelationshipRecord, ...]:
        direction = direction.upper()
        if direction not in {"UPSTREAM", "DOWNSTREAM", "BOTH"}:
            raise RelationshipQueryError(
                "direction must be UPSTREAM, DOWNSTREAM, or BOTH"
            )

        ref_json = self._canonical_json(ref)
        clauses: list[str] = []
        params: list[Any] = []

        if direction in {"DOWNSTREAM", "BOTH"}:
            clauses.append("source_ref_json = ?")
            params.append(ref_json)

        if direction in {"UPSTREAM", "BOTH"}:
            clauses.append("target_ref_json = ?")
            params.append(ref_json)

        where = "(" + " OR ".join(clauses) + ")"

        if relationship_types:
            placeholders = ",".join("?" for _ in relationship_types)
            where += f" AND relationship_type IN ({placeholders})"
            params.extend(relationship_types)

        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT source_ref_json, relationship_type,
                       target_ref_json, created_at, producer_json
                FROM relationships
                WHERE {where}
                ORDER BY created_at ASC, relationship_key ASC
                """,
                params,
            ).fetchall()

        return tuple(
            RelationshipRecord(
                source_ref=json.loads(row["source_ref_json"]),
                relationship_type=row["relationship_type"],
                target_ref=json.loads(row["target_ref_json"]),
                created_at=row["created_at"],
                producer=json.loads(row["producer_json"]),
            )
            for row in rows
        )

    def _initialize(self) -> None:
        with self._connect() as conn:
            current = conn.execute("PRAGMA user_version").fetchone()[0]

            if current > _MIGRATION_VERSION:
                raise CatalogStoreError(
                    f"Catalog schema version {current} is newer than supported "
                    f"version {_MIGRATION_VERSION}"
                )

            if current < 1:
                sql_path = Path(__file__).resolve().parent / "migrations" / "001_initial.sql"
                script = sql_path.read_text(encoding="utf-8")
                conn.executescript(script)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO schema_migrations (version, applied_at)
                    VALUES (?, ?)
                    """,
                    (
                        1,
                        datetime.now(timezone.utc)
                        .isoformat()
                        .replace("+00:00", "Z"),
                    ),
                )
                conn.execute("PRAGMA user_version = 1")
                conn.commit()

    def _insert_or_reconcile_artifact(
        self,
        conn: sqlite3.Connection,
        envelope: ArtifactEnvelope,
    ) -> None:
        ref = envelope.reference()
        row = conn.execute(
            """
            SELECT artifact_type, schema_id, schema_version, created_at,
                   producer_json, provenance_json, lifecycle_state,
                   persistence_class, retention_class,
                   backup_requirement, tags_json
            FROM artifacts
            WHERE artifact_id = ? AND artifact_version = ?
            """,
            (ref.artifact_id, ref.artifact_version),
        ).fetchone()

        values = self._artifact_values(envelope)

        if row is None:
            conn.execute(
                """
                INSERT INTO artifacts (
                    artifact_id, artifact_version, artifact_type,
                    schema_id, schema_version, created_at,
                    producer_json, provenance_json, lifecycle_state,
                    persistence_class, retention_class,
                    backup_requirement, tags_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                values,
            )
            return

        existing = tuple(row)
        incoming = values[2:]

        if existing != incoming:
            raise CatalogConflictError(
                f"Conflicting immutable artifact publication for "
                f"{ref.artifact_id}@{ref.artifact_version}"
            )

    def _insert_or_reconcile_representation(
        self,
        conn: sqlite3.Connection,
        representation: RepresentationRecord,
    ) -> None:
        row = conn.execute(
            """
            SELECT media_type, content_hash, size_bytes,
                   created_at, verification_state
            FROM representations
            WHERE locator = ?
            """,
            (representation.locator,),
        ).fetchone()

        incoming = (
            representation.media_type,
            representation.content_hash,
            representation.size_bytes,
            representation.created_at,
            representation.verification_state,
        )

        if row is not None:
            if tuple(row) != incoming:
                raise CatalogConflictError(
                    f"Conflicting representation at locator "
                    f"{representation.locator}"
                )
            return

        conn.execute(
            """
            INSERT INTO representations (
                artifact_id, artifact_version, locator, media_type,
                content_hash, size_bytes, created_at, verification_state
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                representation.artifact_ref.artifact_id,
                representation.artifact_ref.artifact_version,
                representation.locator,
                representation.media_type,
                representation.content_hash,
                representation.size_bytes,
                representation.created_at,
                representation.verification_state,
            ),
        )

    def _insert_or_reconcile_relationship(
        self,
        conn: sqlite3.Connection,
        relationship: RelationshipRecord,
    ) -> None:
        relationship_key = self._relationship_key(relationship)
        source_json = self._canonical_json(relationship.source_ref)
        target_json = self._canonical_json(relationship.target_ref)
        producer_json = self._canonical_json(relationship.producer)

        row = conn.execute(
            """
            SELECT source_ref_json, relationship_type,
                   target_ref_json, created_at, producer_json
            FROM relationships
            WHERE relationship_key = ?
            """,
            (relationship_key,),
        ).fetchone()

        incoming = (
            source_json,
            relationship.relationship_type,
            target_json,
            relationship.created_at,
            producer_json,
        )

        if row is not None:
            if tuple(row) != incoming:
                raise CatalogConflictError(
                    f"Conflicting relationship publication: {relationship_key}"
                )
            return

        conn.execute(
            """
            INSERT INTO relationships (
                relationship_key, source_ref_json, relationship_type,
                target_ref_json, created_at, producer_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (relationship_key, *incoming),
        )

    def _artifact_values(self, envelope: ArtifactEnvelope) -> tuple[Any, ...]:
        data = envelope.to_dict()
        return (
            data["artifact_id"],
            data["artifact_version"],
            data["artifact_type"],
            data["schema_id"],
            data["schema_version"],
            data["created_at"],
            self._canonical_json(data["producer"]),
            self._canonical_json(data["provenance"]),
            data["lifecycle_state"],
            data["persistence_class"],
            data["retention_class"],
            data["backup_requirement"],
            self._canonical_json(data.get("tags", [])),
        )

    @staticmethod
    def _envelope_from_row(row: sqlite3.Row) -> ArtifactEnvelope:
        producer_data = json.loads(row["producer_json"])
        provenance_data = json.loads(row["provenance_json"])

        return ArtifactEnvelope(
            artifact_id=row["artifact_id"],
            artifact_version=row["artifact_version"],
            artifact_type=row["artifact_type"],
            schema_id=row["schema_id"],
            schema_version=row["schema_version"],
            created_at=datetime.fromisoformat(
                row["created_at"].replace("Z", "+00:00")
            ),
            producer=Producer(
                producer_type=producer_data["producer_type"],
                producer_id=producer_data["producer_id"],
            ),
            provenance=Provenance(
                input_refs=tuple(),
                software_version=provenance_data.get("software_version"),
                model_version=provenance_data.get("model_version"),
                method_id=provenance_data.get("method_id"),
                parameters=provenance_data.get("parameters"),
            ),
            lifecycle_state=row["lifecycle_state"],
            persistence_class=row["persistence_class"],
            retention_class=row["retention_class"],
            backup_requirement=row["backup_requirement"],
            tags=tuple(json.loads(row["tags_json"])),
        )

    @staticmethod
    def _canonical_json(value: Mapping[str, Any] | Sequence[Any]) -> str:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    @classmethod
    def _relationship_key(cls, relationship: RelationshipRecord) -> str:
        material = cls._canonical_json(
            {
                "source_ref": relationship.source_ref,
                "relationship_type": relationship.relationship_type,
                "target_ref": relationship.target_ref,
                "created_at": relationship.created_at,
                "producer": relationship.producer,
            }
        )
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    @contextmanager
    def _connect(self) -> Iterable[sqlite3.Connection]:
        conn = sqlite3.connect(self._database_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
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
