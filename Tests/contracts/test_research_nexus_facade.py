from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from Core.research_nexus import (
    ArtifactReference,
    NexusServices,
    Producer,
    Provenance,
    PublicationCoordinator,
    ResearchNexus,
    RetrievalService,
    create_artifact_envelope,
)
from Core.research_nexus.storage import (
    FilesystemPayloadStore,
    RelationshipRecord,
    SQLiteCatalogStore,
    SQLiteIndexStore,
)


@pytest.fixture
def nexus(tmp_path: Path) -> ResearchNexus:
    catalog = SQLiteCatalogStore(tmp_path / "catalog.sqlite3")
    index = SQLiteIndexStore(tmp_path / "index.sqlite3")
    payloads = FilesystemPayloadStore(tmp_path / "payloads")

    return ResearchNexus(
        NexusServices(
            publication=PublicationCoordinator(
                catalog=catalog,
                payloads=payloads,
                index=index,
            ),
            retrieval=RetrievalService(
                catalog=catalog,
                payloads=payloads,
                index=index,
            ),
        )
    )


def envelope(artifact_id: str = "artifact:test"):
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
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        tags=("AAPL",),
    )


def test_public_facade_publish_get_round_trip(nexus):
    env = envelope()

    published = nexus.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )

    retrieved = nexus.get(published.artifact_ref)

    assert retrieved.envelope == env
    assert retrieved.payload == b"payload"


def test_public_facade_query_returns_domain_envelopes(nexus):
    env = envelope()

    nexus.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )

    assert nexus.query({"tags": "AAPL"}) == (env,)


def test_public_facade_relationship_traversal(nexus):
    env = envelope()

    relationship = RelationshipRecord(
        source_ref={
            "ref_type": "ARTIFACT",
            "ref_id": env.artifact_id,
            "ref_version": "1",
        },
        relationship_type="APPLIES_TO",
        target_ref={"ref_type": "INSTRUMENT", "ref_id": "AAPL"},
        created_at="2026-08-07T10:00:00Z",
        producer={"producer_type": "SYSTEM", "producer_id": "nexus"},
    )

    nexus.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        relationships=(relationship,),
    )

    assert nexus.get_relationships(
        relationship.source_ref,
        direction="DOWNSTREAM",
    ) == (relationship,)


def test_public_facade_verify(nexus):
    env = envelope()

    result = nexus.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
    )

    assert nexus.verify(result.artifact_ref) is None


def test_public_facade_does_not_expose_storage_backends(nexus):
    public_names = {
        name
        for name in dir(nexus)
        if not name.startswith("_")
    }

    forbidden = {
        "catalog",
        "index",
        "payloads",
        "database_path",
        "filesystem_root",
        "sqlite_connection",
    }

    assert forbidden.isdisjoint(public_names)


def test_public_facade_exposes_only_stable_operations():
    public_methods = {
        name
        for name, value in ResearchNexus.__dict__.items()
        if callable(value) and not name.startswith("_")
    }

    assert public_methods == {
        "publish",
        "get",
        "query",
        "get_relationships",
        "verify",
    }


def test_query_limit_is_preserved_through_facade(nexus):
    for artifact_id in ("artifact:a", "artifact:b", "artifact:c"):
        env = envelope(artifact_id)
        nexus.publish(
            envelope=env,
            payload=artifact_id.encode(),
            media_type="application/octet-stream",
            index_fields={"artifact_type": "FINDING"},
        )

    results = nexus.query({"artifact_type": "FINDING"}, limit=2)

    assert len(results) == 2


def test_get_missing_artifact_preserves_typed_service_error(nexus):
    from Core.research_nexus import ArtifactNotFoundError

    with pytest.raises(ArtifactNotFoundError):
        nexus.get(ArtifactReference("artifact:missing", 1))
