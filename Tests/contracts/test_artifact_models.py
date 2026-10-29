from __future__ import annotations

from datetime import datetime, timezone

import pytest

from Core.research_nexus import (
    ArtifactEnvelope,
    ArtifactReference,
    GovernedReference,
    Producer,
    Provenance,
    SchemaValidationError,
    create_artifact_envelope,
    new_artifact_id,
)


def producer() -> Producer:
    return Producer(
        producer_type="ENGINE",
        producer_id="engine:discovery",
    )


def provenance() -> Provenance:
    return Provenance(
        input_refs=(
            ArtifactReference(
                artifact_id="artifact:source-1",
                artifact_version=1,
            ),
        ),
        execution_ref=GovernedReference(
            ref_type="EXECUTION",
            ref_id="execution:01JTEST",
            ref_version="1",
        ),
        software_version="commit:abc123",
        method_id="method:test",
        parameters={"window": 20},
    )


def test_new_artifact_id_is_opaque_location_independent_and_unique():
    first = new_artifact_id()
    second = new_artifact_id()

    assert first.startswith("artifact:")
    assert second.startswith("artifact:")
    assert first != second
    assert "/" not in first
    assert "\\" not in first


def test_artifact_reference_serializes_only_identity_and_version():
    ref = ArtifactReference("artifact:abc", 3)

    assert ref.to_dict() == {
        "artifact_id": "artifact:abc",
        "artifact_version": 3,
    }


def test_governed_reference_omits_absent_version():
    ref = GovernedReference(
        ref_type="POLICY",
        ref_id="policy:research",
    )

    assert ref.to_dict() == {
        "ref_type": "POLICY",
        "ref_id": "policy:research",
    }


def test_provenance_serializes_without_duplicate_producer_state():
    data = provenance().to_dict()

    assert data["input_refs"] == [
        {
            "artifact_id": "artifact:source-1",
            "artifact_version": 1,
        }
    ]
    assert data["execution_ref"]["ref_type"] == "EXECUTION"
    assert data["parameters"] == {"window": 20}
    assert "producer" not in data
    assert "producer_version" not in data


def test_envelope_serializes_to_governed_shape_and_validates():
    envelope = ArtifactEnvelope(
        artifact_id="artifact:test",
        artifact_version=1,
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
        producer=producer(),
        provenance=provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        tags=("AAPL", "relative-volume"),
    )

    envelope.validate()
    data = envelope.to_dict()

    assert data["created_at"] == "2026-08-07T10:00:00Z"
    assert data["tags"] == ["AAPL", "relative-volume"]
    assert "content_hash" not in data
    assert "artifact_family" not in data
    assert "source_refs" not in data


def test_envelope_reference_preserves_logical_identity():
    envelope = create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=producer(),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id="artifact:stable",
        artifact_version=4,
        created_at=datetime(2026, 8, 7, 10, 0, tzinfo=timezone.utc),
    )

    assert envelope.reference() == ArtifactReference(
        artifact_id="artifact:stable",
        artifact_version=4,
    )


def test_create_envelope_generates_identity_and_validates_before_return():
    envelope = create_artifact_envelope(
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        producer=producer(),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        tags=("AAPL",),
    )

    assert envelope.artifact_id.startswith("artifact:")
    assert envelope.artifact_version == 1


def test_create_envelope_does_not_infer_scientific_or_lifecycle_values():
    with pytest.raises(TypeError):
        create_artifact_envelope(
            artifact_type="FINDING",
            schema_id="mts.finding",
            schema_version=1,
            producer=producer(),
            provenance=Provenance(),
            # lifecycle/persistence/retention/backup intentionally absent
        )


def test_invalid_controlled_vocabulary_is_rejected_by_governed_schema():
    with pytest.raises(SchemaValidationError):
        create_artifact_envelope(
            artifact_type="NOT_A_REAL_ARTIFACT_TYPE",
            schema_id="mts.finding",
            schema_version=1,
            producer=producer(),
            provenance=Provenance(),
            lifecycle_state="DRAFT",
            persistence_class="CLASS_II",
            retention_class="SEMI_PERMANENT",
            backup_requirement="REQUIRED",
        )


def test_naive_created_at_is_rejected_without_assuming_timezone():
    envelope = ArtifactEnvelope(
        artifact_id="artifact:test",
        artifact_version=1,
        artifact_type="FINDING",
        schema_id="mts.finding",
        schema_version=1,
        created_at=datetime(2026, 8, 7, 10, 0),
        producer=producer(),
        provenance=Provenance(),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
    )

    with pytest.raises(ValueError, match="offset-aware"):
        envelope.to_dict()
