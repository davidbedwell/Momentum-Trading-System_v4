from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from Core.research_nexus import (
    ArtifactNotFoundError,
    ArtifactReference,
    GovernedReference,
    IntegrityError,
    Producer,
    Provenance,
    PublicationCoordinator,
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
def system(tmp_path: Path):
    catalog = SQLiteCatalogStore(tmp_path / "catalog.sqlite3")
    index = SQLiteIndexStore(tmp_path / "index.sqlite3")
    payloads = FilesystemPayloadStore(tmp_path / "payloads")
    publication = PublicationCoordinator(
        catalog=catalog,
        payloads=payloads,
        index=index,
    )
    retrieval = RetrievalService(
        catalog=catalog,
        payloads=payloads,
        index=index,
    )
    return catalog, index, payloads, publication, retrieval


def rich_envelope(artifact_id: str = "artifact:test"):
    return create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:discovery",
        ),
        provenance=Provenance(
            input_refs=(ArtifactReference("artifact:source", 2),),
            execution_ref=GovernedReference(
                ref_type="EXECUTION",
                ref_id="execution:abc",
                ref_version="1",
            ),
            policy_refs=(
                GovernedReference(
                    ref_type="POLICY",
                    ref_id="policy:research",
                    ref_version="3",
                ),
            ),
            configuration_refs=(
                GovernedReference(
                    ref_type="POLICY",
                    ref_id="configuration:daily",
                    ref_version="7",
                ),
            ),
            software_version="commit:123",
            model_version="model:4",
            method_id="method:rv",
            parameters={"window": 20},
        ),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id=artifact_id,
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        tags=("AAPL", "relative-volume"),
    )


def test_get_returns_envelope_representation_and_payload(system):
    _, _, _, publication, retrieval = system
    env = rich_envelope()

    publication.publish(
        envelope=env,
        payload=b'{"finding":"x"}',
        media_type="application/json",
        index_fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )

    result = retrieval.get(env.reference())

    assert result.envelope.to_dict() == env.to_dict()
    assert result.payload == b'{"finding":"x"}'
    assert result.representation.artifact_ref == env.reference()


def test_catalog_round_trip_preserves_full_provenance(system):
    _, _, _, publication, retrieval = system
    env = rich_envelope()

    publication.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
    )

    loaded = retrieval.get(env.reference()).envelope

    assert loaded.provenance == env.provenance
    assert loaded.to_dict() == env.to_dict()


def test_get_missing_artifact_raises_typed_error(system):
    *_, retrieval = system

    with pytest.raises(ArtifactNotFoundError):
        retrieval.get(ArtifactReference("artifact:missing", 1))


def test_query_hydrates_index_results_from_canonical_catalog(system):
    _, _, _, publication, retrieval = system

    first = rich_envelope("artifact:a")
    second = rich_envelope("artifact:b")

    publication.publish(
        envelope=first,
        payload=b"a",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )
    publication.publish(
        envelope=second,
        payload=b"b",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING", "tags": ["MSFT"]},
    )

    results = retrieval.query({"tags": "AAPL"})

    assert tuple(item.reference() for item in results) == (first.reference(),)


def test_query_limit_is_forwarded_to_index(system):
    _, _, _, publication, retrieval = system

    for artifact_id in ("artifact:a", "artifact:b", "artifact:c"):
        env = rich_envelope(artifact_id)
        publication.publish(
            envelope=env,
            payload=artifact_id.encode(),
            media_type="application/octet-stream",
            index_fields={"artifact_type": "FINDING"},
        )

    assert len(retrieval.query({"artifact_type": "FINDING"}, limit=2)) == 2


def test_relationship_traversal_passes_through_catalog(system):
    catalog, _, _, publication, retrieval = system
    env = rich_envelope()

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

    publication.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        relationships=(relationship,),
    )

    assert retrieval.get_relationships(
        relationship.source_ref,
        direction="DOWNSTREAM",
    ) == (relationship,)


def test_get_detects_corrupted_payload(system):
    _, _, payloads, publication, retrieval = system
    env = rich_envelope()

    result = publication.publish(
        envelope=env,
        payload=b"correct",
        media_type="application/octet-stream",
    )

    path = payloads._path_from_locator(result.representation.locator)
    path.write_bytes(b"corrupt")

    with pytest.raises(IntegrityError):
        retrieval.get(env.reference())


def test_verify_detects_corrupted_payload(system):
    _, _, payloads, publication, retrieval = system
    env = rich_envelope()

    result = publication.publish(
        envelope=env,
        payload=b"correct",
        media_type="application/octet-stream",
    )

    path = payloads._path_from_locator(result.representation.locator)
    path.write_bytes(b"corrupt")

    with pytest.raises(IntegrityError):
        retrieval.verify(env.reference())


def test_get_can_skip_integrity_check_when_explicitly_requested(system):
    _, _, payloads, publication, retrieval = system
    env = rich_envelope()

    result = publication.publish(
        envelope=env,
        payload=b"correct",
        media_type="application/octet-stream",
    )

    path = payloads._path_from_locator(result.representation.locator)
    path.write_bytes(b"corrupt")

    retrieved = retrieval.get(env.reference(), verify=False)

    assert retrieved.payload == b"corrupt"


def test_query_returns_envelopes_not_database_rows(system):
    _, _, _, publication, retrieval = system
    env = rich_envelope()

    publication.publish(
        envelope=env,
        payload=b"payload",
        media_type="application/octet-stream",
        index_fields={"artifact_type": "FINDING"},
    )

    result = retrieval.query({"artifact_type": "FINDING"})

    assert result == (env,)
    assert not hasattr(result[0], "rowid")


def test_integrity_check_rejects_size_mismatch(system):
    catalog, _, payloads, publication, retrieval = system
    env = rich_envelope()

    result = publication.publish(
        envelope=env,
        payload=b"correct",
        media_type="application/octet-stream",
    )

    path = payloads._path_from_locator(result.representation.locator)
    path.write_bytes(b"correcx")  # same length, wrong hash

    with pytest.raises(IntegrityError):
        retrieval.get(env.reference())
