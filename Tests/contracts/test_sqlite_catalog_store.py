from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

import pytest

from Core.research_nexus import (
    ArtifactReference,
    GovernedReference,
    Producer,
    Provenance,
    create_artifact_envelope,
)
from Core.research_nexus.storage import (
    CatalogConflictError,
    CatalogStore,
    PublicationRecord,
    RelationshipQueryError,
    RelationshipRecord,
    RepresentationRecord,
    SQLiteCatalogStore,
)


@pytest.fixture
def catalog(tmp_path: Path) -> SQLiteCatalogStore:
    return SQLiteCatalogStore(tmp_path / "catalog.sqlite3")


def envelope(
    *,
    artifact_id: str = "artifact:test",
    artifact_version: int = 1,
):
    return create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id=artifact_id,
        artifact_version=artifact_version,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        tags=("AAPL",),
    )


def representation(ref: ArtifactReference, locator: str = "nexus-fs:///object"):
    return RepresentationRecord(
        artifact_ref=ref,
        locator=locator,
        media_type="application/json",
        content_hash="sha256:abc",
        size_bytes=3,
        created_at="2026-08-07T10:00:00Z",
        verification_state="VERIFIED",
    )


def test_sqlite_catalog_satisfies_catalog_port(catalog):
    assert isinstance(catalog, CatalogStore)


def test_migration_initializes_schema_version(catalog):
    with sqlite3.connect(catalog.database_path) as conn:
        user_version = conn.execute("PRAGMA user_version").fetchone()[0]
        applied = conn.execute(
            "SELECT version FROM schema_migrations ORDER BY version"
        ).fetchall()

    assert user_version == 1
    assert applied == [(1,)]


def test_register_and_get_artifact(catalog):
    env = envelope()
    rep = representation(env.reference())

    catalog.register_artifact(env, rep)

    loaded = catalog.get_artifact(env.reference())

    assert loaded is not None
    assert loaded.artifact_id == env.artifact_id
    assert loaded.artifact_version == env.artifact_version
    assert loaded.artifact_type == env.artifact_type


def test_artifact_exists(catalog):
    env = envelope()
    catalog.register_artifact(env, representation(env.reference()))

    assert catalog.artifact_exists(env.reference()) is True
    assert catalog.artifact_exists(
        ArtifactReference("artifact:missing", 1)
    ) is False


def test_get_representation(catalog):
    env = envelope()
    rep = representation(env.reference())

    catalog.register_artifact(env, rep)

    loaded = catalog.get_representation(env.reference())

    assert loaded == rep


def test_same_immutable_artifact_is_idempotent(catalog):
    env = envelope()
    rep = representation(env.reference())

    catalog.register_artifact(env, rep)
    catalog.register_artifact(env, rep)

    assert catalog.artifact_exists(env.reference())


def test_conflicting_immutable_artifact_is_rejected(catalog):
    env = envelope()
    rep = representation(env.reference())
    catalog.register_artifact(env, rep)

    conflicting = create_artifact_envelope(
        artifact_type="EVIDENCE",
        schema_id="mts.finding",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id=env.artifact_id,
        artifact_version=env.artifact_version,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        tags=("AAPL",),
    )

    with pytest.raises(CatalogConflictError):
        catalog.register_artifact(
            conflicting,
            representation(conflicting.reference()),
        )


def test_representation_must_match_envelope_identity(catalog):
    env = envelope()

    with pytest.raises(Exception, match="does not match"):
        catalog.register_artifact(
            env,
            representation(ArtifactReference("artifact:other", 1)),
        )


def test_relationship_round_trip_and_direction(catalog):
    env = envelope()
    rep = representation(env.reference())

    relation = RelationshipRecord(
        source_ref={
            "ref_type": "ARTIFACT",
            "ref_id": env.artifact_id,
            "ref_version": str(env.artifact_version),
        },
        relationship_type="GENERATED_BY",
        target_ref={
            "ref_type": "EXECUTION",
            "ref_id": "execution:1",
        },
        created_at="2026-08-07T10:00:00Z",
        producer={
            "producer_type": "SYSTEM",
            "producer_id": "nexus",
        },
    )

    catalog.register_artifact(env, rep, relationships=(relation,))

    downstream = catalog.get_relationships(
        relation.source_ref,
        direction="DOWNSTREAM",
    )
    upstream = catalog.get_relationships(
        relation.target_ref,
        direction="UPSTREAM",
    )

    assert downstream == (relation,)
    assert upstream == (relation,)


def test_relationship_filter(catalog):
    env = envelope()
    rep = representation(env.reference())

    a = RelationshipRecord(
        source_ref={"ref_type": "ARTIFACT", "ref_id": env.artifact_id},
        relationship_type="DERIVED_FROM",
        target_ref={"ref_type": "ARTIFACT", "ref_id": "artifact:source"},
        created_at="2026-08-07T10:00:00Z",
        producer={"producer_type": "SYSTEM", "producer_id": "nexus"},
    )
    b = RelationshipRecord(
        source_ref={"ref_type": "ARTIFACT", "ref_id": env.artifact_id},
        relationship_type="APPLIES_TO",
        target_ref={"ref_type": "INSTRUMENT", "ref_id": "AAPL"},
        created_at="2026-08-07T10:00:01Z",
        producer={"producer_type": "SYSTEM", "producer_id": "nexus"},
    )

    catalog.register_artifact(env, rep, relationships=(a, b))

    matches = catalog.get_relationships(
        a.source_ref,
        direction="DOWNSTREAM",
        relationship_types=("APPLIES_TO",),
    )

    assert matches == (b,)


def test_invalid_relationship_direction_rejected(catalog):
    with pytest.raises(RelationshipQueryError):
        catalog.get_relationships(
            {"ref_type": "ARTIFACT", "ref_id": "artifact:test"},
            direction="SIDEWAYS",
        )


def test_publication_record_is_persisted(catalog):
    env = envelope()
    publication = PublicationRecord(
        artifact_ref=env.reference(),
        publication_state="PUBLISHED",
        recorded_at="2026-08-07T10:00:00Z",
    )

    catalog.register_artifact(
        env,
        representation(env.reference()),
        publication=publication,
    )

    with sqlite3.connect(catalog.database_path) as conn:
        row = conn.execute(
            """
            SELECT publication_state, recorded_at
            FROM publication_records
            WHERE artifact_id = ? AND artifact_version = ?
            """,
            (env.artifact_id, env.artifact_version),
        ).fetchone()

    assert row == ("PUBLISHED", "2026-08-07T10:00:00Z")


def test_compound_registration_is_atomic(catalog):
    env = envelope()
    rep = representation(env.reference())

    good = RelationshipRecord(
        source_ref={"ref_type": "ARTIFACT", "ref_id": env.artifact_id},
        relationship_type="DERIVED_FROM",
        target_ref={"ref_type": "ARTIFACT", "ref_id": "artifact:source"},
        created_at="2026-08-07T10:00:00Z",
        producer={"producer_type": "SYSTEM", "producer_id": "nexus"},
    )

    bad_rep = RepresentationRecord(
        artifact_ref=env.reference(),
        locator=rep.locator,
        media_type="application/json",
        content_hash="sha256:DIFFERENT",
        size_bytes=99,
        created_at=rep.created_at,
        verification_state="VERIFIED",
    )

    catalog.register_artifact(env, rep)

    # Different artifact/version reusing same locator with conflicting metadata
    # must fail, and the second artifact must not become visible.
    second = envelope(artifact_id="artifact:second")

    with pytest.raises(CatalogConflictError):
        catalog.register_artifact(
            second,
            RepresentationRecord(
                artifact_ref=second.reference(),
                locator=bad_rep.locator,
                media_type=bad_rep.media_type,
                content_hash=bad_rep.content_hash,
                size_bytes=bad_rep.size_bytes,
                created_at=bad_rep.created_at,
                verification_state=bad_rep.verification_state,
            ),
            relationships=(good,),
        )

    assert catalog.artifact_exists(second.reference()) is False


def test_catalog_tables_do_not_require_row_ids(catalog):
    with sqlite3.connect(catalog.database_path) as conn:
        artifact_columns = {
            row[1]
            for row in conn.execute("PRAGMA table_info(artifacts)").fetchall()
        }
        representation_columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(representations)"
            ).fetchall()
        }

    assert "id" not in artifact_columns
    assert "row_id" not in artifact_columns
    assert "id" not in representation_columns
    assert "row_id" not in representation_columns
