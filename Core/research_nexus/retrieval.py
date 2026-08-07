from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from Core.research_nexus.models import ArtifactEnvelope, ArtifactReference
from Core.research_nexus.storage import (
    CatalogStore,
    IndexStore,
    PayloadStore,
    RelationshipRecord,
    RepresentationRecord,
)


class RetrievalError(RuntimeError):
    """Base class for governed Nexus retrieval failures."""


class ArtifactNotFoundError(RetrievalError):
    """Raised when a requested canonical artifact does not exist."""


class RepresentationNotFoundError(RetrievalError):
    """Raised when a canonical artifact has no registered representation."""


class IntegrityError(RetrievalError):
    """Raised when retrieved representation bytes fail integrity checks."""


@dataclass(frozen=True, slots=True)
class RetrievedArtifact:
    envelope: ArtifactEnvelope
    representation: RepresentationRecord
    payload: bytes


class RetrievalService:
    """Backend-neutral retrieval/query service over Nexus storage ports."""

    def __init__(
        self,
        *,
        catalog: CatalogStore,
        payloads: PayloadStore,
        index: IndexStore,
    ) -> None:
        self._catalog = catalog
        self._payloads = payloads
        self._index = index

    def get(
        self,
        artifact_ref: ArtifactReference,
        *,
        verify: bool = True,
    ) -> RetrievedArtifact:
        envelope = self._catalog.get_artifact(artifact_ref)
        if envelope is None:
            raise ArtifactNotFoundError(
                f"Artifact not found: "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        representation = self._catalog.get_representation(artifact_ref)
        if representation is None:
            raise RepresentationNotFoundError(
                f"Representation not found: "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        payload = self._payloads.get(representation.locator)

        if verify:
            self._verify_payload(representation, payload)

        return RetrievedArtifact(
            envelope=envelope,
            representation=representation,
            payload=payload,
        )

    def query(
        self,
        criteria: Mapping[str, Any],
        *,
        limit: int | None = None,
    ) -> tuple[ArtifactEnvelope, ...]:
        refs = self._index.search(criteria, limit=limit)
        results: list[ArtifactEnvelope] = []

        for ref in refs:
            envelope = self._catalog.get_artifact(ref)
            if envelope is None:
                raise ArtifactNotFoundError(
                    "Index references missing canonical artifact: "
                    f"{ref.artifact_id}@{ref.artifact_version}"
                )
            results.append(envelope)

        return tuple(results)

    def get_relationships(
        self,
        ref: Mapping[str, Any],
        *,
        direction: str = "BOTH",
        relationship_types: Sequence[str] = (),
    ) -> tuple[RelationshipRecord, ...]:
        return self._catalog.get_relationships(
            ref,
            direction=direction,
            relationship_types=relationship_types,
        )

    def verify(self, artifact_ref: ArtifactReference) -> None:
        retrieved = self.get(artifact_ref, verify=False)
        self._verify_payload(
            retrieved.representation,
            retrieved.payload,
        )

    @staticmethod
    def _verify_payload(
        representation: RepresentationRecord,
        payload: bytes,
    ) -> None:
        if not representation.content_hash.startswith("sha256:"):
            raise IntegrityError(
                f"Unsupported content hash: {representation.content_hash}"
            )

        expected = representation.content_hash.removeprefix("sha256:")
        actual = hashlib.sha256(payload).hexdigest()

        if actual != expected:
            raise IntegrityError(
                f"Payload integrity failure for "
                f"{representation.artifact_ref.artifact_id}@"
                f"{representation.artifact_ref.artifact_version}"
            )

        if len(payload) != representation.size_bytes:
            raise IntegrityError(
                f"Payload size mismatch for "
                f"{representation.artifact_ref.artifact_id}@"
                f"{representation.artifact_ref.artifact_version}"
            )
