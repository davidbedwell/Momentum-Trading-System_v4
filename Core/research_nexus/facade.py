from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from Core.research_nexus.models import ArtifactEnvelope, ArtifactReference
from Core.research_nexus.publication import (
    PublicationCoordinator,
    PublicationResult,
)
from Core.research_nexus.retrieval import (
    RetrievedArtifact,
    RetrievalService,
)
from Core.research_nexus.storage import RelationshipRecord


@dataclass(frozen=True, slots=True)
class NexusServices:
    """Internal service bundle used to compose the public Nexus façade."""

    publication: PublicationCoordinator
    retrieval: RetrievalService


class ResearchNexus:
    """Stable engine-facing API for governed Research Nexus operations.

    Engines interact with this façade rather than constructing or depending on
    catalog, index, payload, SQLite, filesystem, or migration implementations.
    """

    def __init__(self, services: NexusServices) -> None:
        self._services = services

    def publish(
        self,
        *,
        envelope: ArtifactEnvelope,
        payload: bytes,
        media_type: str,
        relationships: Sequence[RelationshipRecord] = (),
        index_fields: Mapping[str, Any] | None = None,
        publication_state: str = "PUBLISHED",
    ) -> PublicationResult:
        return self._services.publication.publish(
            envelope=envelope,
            payload=payload,
            media_type=media_type,
            relationships=relationships,
            index_fields=index_fields,
            publication_state=publication_state,
        )

    def get(
        self,
        artifact_ref: ArtifactReference,
        *,
        verify: bool = True,
    ) -> RetrievedArtifact:
        return self._services.retrieval.get(
            artifact_ref,
            verify=verify,
        )

    def query(
        self,
        criteria: Mapping[str, Any],
        *,
        limit: int | None = None,
    ) -> tuple[ArtifactEnvelope, ...]:
        return self._services.retrieval.query(
            criteria,
            limit=limit,
        )

    def get_relationships(
        self,
        ref: Mapping[str, Any],
        *,
        direction: str = "BOTH",
        relationship_types: Sequence[str] = (),
    ) -> tuple[RelationshipRecord, ...]:
        return self._services.retrieval.get_relationships(
            ref,
            direction=direction,
            relationship_types=relationship_types,
        )

    def verify(self, artifact_ref: ArtifactReference) -> None:
        self._services.retrieval.verify(artifact_ref)
