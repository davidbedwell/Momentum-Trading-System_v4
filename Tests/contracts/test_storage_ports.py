from __future__ import annotations

from typing import Any, Mapping, Sequence

from Core.research_nexus.models import ArtifactEnvelope, ArtifactReference
from Core.research_nexus.storage import (
    CatalogStore,
    IndexDocument,
    IndexStore,
    PayloadStore,
    PayloadWriteResult,
    PublicationRecord,
    RelationshipRecord,
    RepresentationRecord,
)


class FakeCatalog:
    def get_artifact(self, artifact_ref: ArtifactReference) -> ArtifactEnvelope | None:
        return None

    def register_artifact(
        self,
        envelope: ArtifactEnvelope,
        representation: RepresentationRecord,
        relationships: Sequence[RelationshipRecord] = (),
        publication: PublicationRecord | None = None,
    ) -> None:
        return None

    def artifact_exists(self, artifact_ref: ArtifactReference) -> bool:
        return False

    def get_representation(
        self,
        artifact_ref: ArtifactReference,
    ) -> RepresentationRecord | None:
        return None

    def add_relationship(self, relationship: RelationshipRecord) -> None:
        return None

    def get_relationships(
        self,
        ref: Mapping[str, Any],
        *,
        direction: str = "BOTH",
        relationship_types: Sequence[str] = (),
    ) -> tuple[RelationshipRecord, ...]:
        return ()


class FakeIndex:
    def upsert(self, document: IndexDocument) -> None:
        return None

    def remove(self, artifact_ref: ArtifactReference) -> None:
        return None

    def search(
        self,
        criteria: Mapping[str, Any],
        *,
        limit: int | None = None,
    ) -> tuple[ArtifactReference, ...]:
        return ()


class FakePayload:
    def put(
        self,
        artifact_ref: ArtifactReference,
        payload: bytes,
        *,
        media_type: str,
    ) -> PayloadWriteResult:
        return PayloadWriteResult(
            locator="memory://payload",
            media_type=media_type,
            content_hash="sha256:test",
            size_bytes=len(payload),
            created_at="2026-08-07T10:00:00Z",
        )

    def get(self, locator: str) -> bytes:
        return b""

    def exists(self, locator: str) -> bool:
        return True

    def delete(self, locator: str) -> None:
        return None


def test_catalog_store_is_runtime_checkable_protocol():
    assert isinstance(FakeCatalog(), CatalogStore)


def test_index_store_is_runtime_checkable_protocol():
    assert isinstance(FakeIndex(), IndexStore)


def test_payload_store_is_runtime_checkable_protocol():
    assert isinstance(FakePayload(), PayloadStore)


def test_representation_record_keeps_physical_identity_separate():
    record = RepresentationRecord(
        artifact_ref=ArtifactReference("artifact:test", 1),
        locator="file:///tmp/object",
        media_type="application/json",
        content_hash="sha256:abc",
        size_bytes=10,
        created_at="2026-08-07T10:00:00Z",
        verification_state="VERIFIED",
    )

    assert record.artifact_ref.artifact_id == "artifact:test"
    assert record.locator != record.artifact_ref.artifact_id


def test_payload_write_result_contains_no_artifact_identity():
    result = PayloadWriteResult(
        locator="file:///tmp/object",
        media_type="application/json",
        content_hash="sha256:abc",
        size_bytes=10,
        created_at="2026-08-07T10:00:00Z",
    )

    assert not hasattr(result, "artifact_id")
    assert not hasattr(result, "artifact_ref")


def test_index_document_is_backend_neutral():
    doc = IndexDocument(
        artifact_ref=ArtifactReference("artifact:test", 1),
        fields={"artifact_type": "FINDING", "tags": ["AAPL"]},
    )

    assert doc.fields["artifact_type"] == "FINDING"
    assert not hasattr(doc, "row_id")
    assert not hasattr(doc, "table_name")


def test_relationship_record_uses_governed_reference_shapes():
    record = RelationshipRecord(
        source_ref={"ref_type": "ARTIFACT", "ref_id": "artifact:a"},
        relationship_type="DERIVED_FROM",
        target_ref={"ref_type": "EXECUTION", "ref_id": "execution:1"},
        created_at="2026-08-07T10:00:00Z",
        producer={"producer_type": "SYSTEM", "producer_id": "nexus"},
    )

    assert record.source_ref["ref_type"] == "ARTIFACT"
    assert record.target_ref["ref_type"] == "EXECUTION"


def test_ports_do_not_expose_sqlite_or_filesystem_specific_contracts():
    catalog_names = set(CatalogStore.__dict__)
    index_names = set(IndexStore.__dict__)
    payload_names = set(PayloadStore.__dict__)

    forbidden = {
        "row_id",
        "table",
        "cursor",
        "sqlite_connection",
        "filesystem_root",
        "absolute_path",
    }

    assert forbidden.isdisjoint(catalog_names)
    assert forbidden.isdisjoint(index_names)
    assert forbidden.isdisjoint(payload_names)
