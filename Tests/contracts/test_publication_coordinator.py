from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from Core.research_nexus import (
    Producer,
    Provenance,
    PublicationConflictError,
    PublicationCoordinator,
    PublicationVerificationError,
    SchemaValidationError,
    create_artifact_envelope,
)
from Core.research_nexus.storage import (
    FilesystemPayloadStore,
    RelationshipRecord,
    SQLiteCatalogStore,
    SQLiteIndexStore,
)


@pytest.fixture
def components(tmp_path: Path):
    catalog = SQLiteCatalogStore(tmp_path / "catalog.sqlite3")
    index = SQLiteIndexStore(tmp_path / "index.sqlite3")
    payloads = FilesystemPayloadStore(tmp_path / "payloads")
    coordinator = PublicationCoordinator(
        catalog=catalog,
        payloads=payloads,
        index=index,
    )
    return catalog, index, payloads, coordinator


def envelope(
    *,
    artifact_id: str = "artifact:test",
    artifact_type: str = "FINDING",
):
    return create_artifact_envelope(
        artifact_type=artifact_type,
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


def test_publish_makes_artifact_canonical_and_queryable(components):
    catalog, index, payloads, coordinator = components
    env = envelope()

    result = coordinator.publish(
        envelope=env,
        payload=b'{"finding":"x"}',
        media_type="application/json",
        index_fields={
            "artifact_type": "FINDING",
            "tags": ["AAPL"],
        },
    )

    assert result.reconciled is False
    assert catalog.artifact_exists(env.reference())
    assert payloads.exists(result.representation.locator)
    assert index.search({"tags": "AAPL"}) == (env.reference(),)


def test_publish_persists_relationships(components):
    catalog, _, _, coordinator = components
    env = envelope()

    relation = RelationshipRecord(
        source_ref={
            "ref_type": "ARTIFACT",
            "ref_id": env.artifact_id,
            "ref_version": "1",
        },
        relationship_type="APPLIES_TO",
        target_ref={
            "ref_type": "INSTRUMENT",
            "ref_id": "AAPL",
        },
        created_at="2026-08-07T10:00:00Z",
        producer={
            "producer_type": "SYSTEM",
            "producer_id": "nexus",
        },
    )

    coordinator.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        relationships=(relation,),
    )

    assert catalog.get_relationships(
        relation.source_ref,
        direction="DOWNSTREAM",
    ) == (relation,)


def test_same_envelope_same_payload_reconciles_idempotently(components):
    catalog, _, _, coordinator = components
    env = envelope()

    first = coordinator.publish(
        envelope=env,
        payload=b"same",
        media_type="application/octet-stream",
    )
    second = coordinator.publish(
        envelope=env,
        payload=b"same",
        media_type="application/octet-stream",
    )

    assert first.reconciled is False
    assert second.reconciled is True
    assert first.representation.content_hash == second.representation.content_hash
    assert catalog.artifact_exists(env.reference())


def test_same_identity_different_payload_is_rejected(components):
    _, _, _, coordinator = components
    env = envelope()

    coordinator.publish(
        envelope=env,
        payload=b"first",
        media_type="application/octet-stream",
    )

    with pytest.raises(PublicationConflictError):
        coordinator.publish(
            envelope=env,
            payload=b"second",
            media_type="application/octet-stream",
        )


def test_same_identity_different_envelope_is_rejected(components):
    _, _, _, coordinator = components
    first = envelope()
    second = envelope(artifact_type="EVIDENCE")

    coordinator.publish(
        envelope=first,
        payload=b"same",
        media_type="application/octet-stream",
    )

    with pytest.raises(PublicationConflictError):
        coordinator.publish(
            envelope=second,
            payload=b"same",
            media_type="application/octet-stream",
        )


def test_invalid_envelope_fails_before_canonical_registration(components):
    from Core.research_nexus import ArtifactEnvelope

    catalog, _, _, coordinator = components

    env = ArtifactEnvelope(
        artifact_id="artifact:invalid",
        artifact_version=1,
        artifact_type="NOT_REAL",
        schema_id="mts.finding",
        schema_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
    )

    with pytest.raises(SchemaValidationError):
        coordinator.publish(
            envelope=env,
            payload=b"payload",
            media_type="application/octet-stream",
        )

    assert catalog.artifact_exists(env.reference()) is False


def test_catalog_failure_cleans_uncommitted_payload(tmp_path):
    class FailingCatalog:
        def get_artifact(self, artifact_ref):
            return None

        def register_artifact(self, *args, **kwargs):
            raise RuntimeError("catalog write failed")

        def artifact_exists(self, artifact_ref):
            return False

        def get_representation(self, artifact_ref):
            return None

        def add_relationship(self, relationship):
            return None

        def get_relationships(self, *args, **kwargs):
            return ()

    index = SQLiteIndexStore(tmp_path / "index.sqlite3")
    payloads = FilesystemPayloadStore(tmp_path / "payloads")
    coordinator = PublicationCoordinator(
        catalog=FailingCatalog(),
        payloads=payloads,
        index=index,
    )
    env = envelope()

    with pytest.raises(RuntimeError, match="catalog write failed"):
        coordinator.publish(
            envelope=env,
            payload=b"orphan",
            media_type="application/octet-stream",
        )

    assert list(payloads.root.rglob("*")) == []


def test_index_failure_does_not_make_canonical_artifact_disappear(tmp_path):
    class FailingIndex:
        def upsert(self, document):
            raise RuntimeError("index failed")

        def remove(self, artifact_ref):
            return None

        def search(self, criteria, *, limit=None):
            return ()

    catalog = SQLiteCatalogStore(tmp_path / "catalog.sqlite3")
    payloads = FilesystemPayloadStore(tmp_path / "payloads")
    coordinator = PublicationCoordinator(
        catalog=catalog,
        payloads=payloads,
        index=FailingIndex(),
    )
    env = envelope()

    with pytest.raises(RuntimeError, match="index failed"):
        coordinator.publish(
            envelope=env,
            payload=b"payload",
            media_type="application/octet-stream",
            index_fields={"artifact_type": "FINDING"},
        )

    assert catalog.artifact_exists(env.reference()) is True


def test_post_commit_payload_loss_is_detected(components):
    catalog, _, payloads, coordinator = components
    env = envelope()

    result = coordinator.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
    )

    payloads.delete(result.representation.locator)

    with pytest.raises(PublicationVerificationError):
        coordinator._verify(env.reference(), result.representation)


def test_publication_result_returns_stable_artifact_reference(components):
    _, _, _, coordinator = components
    env = envelope(artifact_id="artifact:stable")

    result = coordinator.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
    )

    assert result.artifact_ref == env.reference()


def test_index_is_optional_for_canonical_publication(components):
    catalog, index, _, coordinator = components
    env = envelope()

    coordinator.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        index_fields=None,
    )

    assert catalog.artifact_exists(env.reference())
    assert index.search({}) == ()


def test_media_type_change_for_same_identity_is_conflict(components):
    _, _, _, coordinator = components
    env = envelope()

    coordinator.publish(
        envelope=env,
        payload=b"same",
        media_type="application/octet-stream",
    )

    with pytest.raises(PublicationConflictError):
        coordinator.publish(
            envelope=env,
            payload=b"same",
            media_type="text/plain",
        )


def test_conflicting_retry_cleans_noncanonical_payload(components):
    _, _, payloads, coordinator = components
    env = envelope()

    first = coordinator.publish(
        envelope=env,
        payload=b"first",
        media_type="application/octet-stream",
    )

    with pytest.raises(PublicationConflictError):
        coordinator.publish(
            envelope=env,
            payload=b"second",
            media_type="application/octet-stream",
        )

    files = [p for p in payloads.root.rglob("*") if p.is_file()]
    assert len(files) == 1
    assert payloads.get(first.representation.locator) == b"first"
