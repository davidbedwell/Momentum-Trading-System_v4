from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

from Core.research_nexus.errors import SchemaValidationError
from Core.research_nexus.models import ArtifactEnvelope, ArtifactReference
from Core.research_nexus.storage import (
    CatalogConflictError,
    CatalogStore,
    IndexDocument,
    IndexStore,
    PayloadStore,
    PublicationRecord,
    RelationshipRecord,
    RepresentationRecord,
)
from Core.research_nexus.validation import SchemaValidator


class PublicationError(RuntimeError):
    """Base class for governed publication failures."""


class PublicationConflictError(PublicationError):
    """Raised when immutable publication semantics conflict."""


class PublicationVerificationError(PublicationError):
    """Raised when a completed publication cannot be verified."""


@dataclass(frozen=True, slots=True)
class PublicationResult:
    artifact_ref: ArtifactReference
    representation: RepresentationRecord
    publication_state: str
    reconciled: bool


class PublicationCoordinator:
    """Coordinate one governed Nexus publication.

    Canonical visibility is established only through CatalogStore registration.
    Payload bytes may exist before catalog commit, but remain non-canonical until
    the catalog transaction succeeds. Indexing occurs after canonical commit and
    is therefore recoverable/rebuildable from canonical catalog state.
    """

    def __init__(
        self,
        *,
        catalog: CatalogStore,
        payloads: PayloadStore,
        index: IndexStore,
        validator: SchemaValidator | None = None,
    ) -> None:
        self._catalog = catalog
        self._payloads = payloads
        self._index = index
        self._validator = validator or SchemaValidator()

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
        self._validate_envelope(envelope)

        ref = envelope.reference()
        existing = self._catalog.get_artifact(ref)

        # Serialize/write first so immutable-content identity can be compared
        # against any existing canonical representation.
        write_result = self._payloads.put(
            ref,
            payload,
            media_type=media_type,
        )

        representation = RepresentationRecord(
            artifact_ref=ref,
            locator=write_result.locator,
            media_type=write_result.media_type,
            content_hash=write_result.content_hash,
            size_bytes=write_result.size_bytes,
            created_at=write_result.created_at,
            verification_state="VERIFIED",
        )

        if existing is not None:
            try:
                self._reconcile_existing(
                    expected_envelope=envelope,
                    artifact_ref=ref,
                    representation=representation,
                )
            except Exception:
                self._cleanup_uncommitted_if_noncanonical(
                    artifact_ref=ref,
                    representation=representation,
                )
                raise

            if index_fields is not None:
                self._index.upsert(
                    IndexDocument(
                        artifact_ref=ref,
                        fields=dict(index_fields),
                    )
                )

            self._verify(ref, representation)

            return PublicationResult(
                artifact_ref=ref,
                representation=representation,
                publication_state=publication_state,
                reconciled=True,
            )

        publication = PublicationRecord(
            artifact_ref=ref,
            publication_state=publication_state,
            recorded_at=self._now(),
        )

        try:
            self._catalog.register_artifact(
                envelope,
                representation,
                relationships=relationships,
                publication=publication,
            )
        except CatalogConflictError as exc:
            # A concurrent/ambiguous publication may have completed between the
            # initial existence check and registration. Re-read and reconcile.
            current = self._catalog.get_artifact(ref)
            if current is None:
                self._cleanup_uncommitted(representation)
                raise PublicationConflictError(str(exc)) from exc

            try:
                self._reconcile_existing(
                    expected_envelope=envelope,
                    artifact_ref=ref,
                    representation=representation,
                )
            except Exception:
                self._cleanup_uncommitted(representation)
                raise

            reconciled = True
        except Exception:
            self._cleanup_uncommitted(representation)
            raise
        else:
            reconciled = False

        if index_fields is not None:
            self._index.upsert(
                IndexDocument(
                    artifact_ref=ref,
                    fields=dict(index_fields),
                )
            )

        self._verify(ref, representation)

        return PublicationResult(
            artifact_ref=ref,
            representation=representation,
            publication_state=publication_state,
            reconciled=reconciled,
        )

    def _validate_envelope(self, envelope: ArtifactEnvelope) -> None:
        try:
            envelope.validate(self._validator)
        except SchemaValidationError:
            raise
        except Exception as exc:
            raise PublicationError(
                f"Artifact envelope validation failed: {exc}"
            ) from exc

    def _reconcile_existing(
        self,
        *,
        expected_envelope: ArtifactEnvelope,
        artifact_ref: ArtifactReference,
        representation: RepresentationRecord,
    ) -> None:
        canonical = self._catalog.get_artifact(artifact_ref)
        if canonical is None:
            raise PublicationConflictError(
                f"Expected existing artifact disappeared: "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        if canonical.to_dict() != expected_envelope.to_dict():
            raise PublicationConflictError(
                f"Conflicting immutable artifact envelope for "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        canonical_representation = self._catalog.get_representation(artifact_ref)
        if canonical_representation is None:
            raise PublicationVerificationError(
                f"Canonical artifact has no representation: "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        if (
            canonical_representation.content_hash != representation.content_hash
            or canonical_representation.size_bytes != representation.size_bytes
            or canonical_representation.media_type != representation.media_type
        ):
            raise PublicationConflictError(
                f"Conflicting immutable payload for "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

    def _verify(
        self,
        artifact_ref: ArtifactReference,
        representation: RepresentationRecord,
    ) -> None:
        if not self._catalog.artifact_exists(artifact_ref):
            raise PublicationVerificationError(
                f"Catalog does not contain committed artifact "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        canonical_representation = self._catalog.get_representation(artifact_ref)
        if canonical_representation is None:
            raise PublicationVerificationError(
                f"Catalog does not contain representation for "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        if not self._payloads.exists(canonical_representation.locator):
            raise PublicationVerificationError(
                f"Payload is missing for committed artifact "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

        payload = self._payloads.get(canonical_representation.locator)
        digest = hashlib.sha256(payload).hexdigest()
        expected = canonical_representation.content_hash

        if expected != f"sha256:{digest}":
            raise PublicationVerificationError(
                f"Payload hash verification failed for "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            )

    def _cleanup_uncommitted_if_noncanonical(
        self,
        *,
        artifact_ref: ArtifactReference,
        representation: RepresentationRecord,
    ) -> None:
        canonical = self._catalog.get_representation(artifact_ref)
        if canonical is not None and canonical.locator == representation.locator:
            return
        self._cleanup_uncommitted(representation)

    def _cleanup_uncommitted(
        self,
        representation: RepresentationRecord,
    ) -> None:
        try:
            if self._payloads.exists(representation.locator):
                self._payloads.delete(representation.locator)
        except Exception:
            # Cleanup failure must not convert a failed canonical registration
            # into a success. Recovery tooling can remove abandoned payloads.
            pass

    @staticmethod
    def _now() -> str:
        return (
            datetime.now(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
