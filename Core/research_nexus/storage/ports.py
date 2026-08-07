from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence, runtime_checkable

from Core.research_nexus.models import ArtifactEnvelope, ArtifactReference


@dataclass(frozen=True, slots=True)
class RepresentationRecord:
    """Physical representation metadata for one artifact version."""

    artifact_ref: ArtifactReference
    locator: str
    media_type: str
    content_hash: str
    size_bytes: int
    created_at: str
    verification_state: str


@dataclass(frozen=True, slots=True)
class RelationshipRecord:
    """Governed relationship edge between two governed identities."""

    source_ref: Mapping[str, Any]
    relationship_type: str
    target_ref: Mapping[str, Any]
    created_at: str
    producer: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class PublicationRecord:
    """Minimal catalog-side publication audit fact."""

    artifact_ref: ArtifactReference
    publication_state: str
    recorded_at: str


@dataclass(frozen=True, slots=True)
class PayloadWriteResult:
    """Result returned by a payload backend after durable representation write."""

    locator: str
    media_type: str
    content_hash: str
    size_bytes: int
    created_at: str


@dataclass(frozen=True, slots=True)
class IndexDocument:
    """Backend-neutral index entry used for discovery/retrieval."""

    artifact_ref: ArtifactReference
    fields: Mapping[str, Any]


@runtime_checkable
class CatalogStore(Protocol):
    """Persistence port for canonical Nexus metadata.

    Implementations may use SQLite, PostgreSQL, or another suitable backend.
    Callers depend only on these semantics, never on backend row/layout details.
    """

    def get_artifact(self, artifact_ref: ArtifactReference) -> ArtifactEnvelope | None:
        ...

    def register_artifact(
        self,
        envelope: ArtifactEnvelope,
        representation: RepresentationRecord,
        relationships: Sequence[RelationshipRecord] = (),
        publication: PublicationRecord | None = None,
    ) -> None:
        ...

    def artifact_exists(self, artifact_ref: ArtifactReference) -> bool:
        ...

    def get_representation(
        self,
        artifact_ref: ArtifactReference,
    ) -> RepresentationRecord | None:
        ...

    def add_relationship(self, relationship: RelationshipRecord) -> None:
        ...

    def get_relationships(
        self,
        ref: Mapping[str, Any],
        *,
        direction: str = "BOTH",
        relationship_types: Sequence[str] = (),
    ) -> tuple[RelationshipRecord, ...]:
        ...


@runtime_checkable
class IndexStore(Protocol):
    """Persistence port for query/discovery indexes.

    The logical port is permanent. Its implementation may initially be SQLite
    and later move to a dedicated search/columnar/index technology.
    """

    def upsert(self, document: IndexDocument) -> None:
        ...

    def remove(self, artifact_ref: ArtifactReference) -> None:
        ...

    def search(
        self,
        criteria: Mapping[str, Any],
        *,
        limit: int | None = None,
    ) -> tuple[ArtifactReference, ...]:
        ...


@runtime_checkable
class PayloadStore(Protocol):
    """Persistence port for artifact representation bytes.

    The payload backend owns physical placement. Locators returned here are
    implementation values, not semantic artifact identity.
    """

    def put(
        self,
        artifact_ref: ArtifactReference,
        payload: bytes,
        *,
        media_type: str,
    ) -> PayloadWriteResult:
        ...

    def get(self, locator: str) -> bytes:
        ...

    def exists(self, locator: str) -> bool:
        ...

    def delete(self, locator: str) -> None:
        ...
