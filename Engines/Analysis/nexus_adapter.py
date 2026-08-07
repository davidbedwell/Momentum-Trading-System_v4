from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from Core.research_nexus import (
    ArtifactReference,
    ResearchNexus,
    SchemaValidationError,
    SchemaValidator,
)


class AnalysisNexusAdapterError(RuntimeError):
    """Base class for Analysis-side Research Nexus boundary failures."""


class UnsupportedRepresentationError(AnalysisNexusAdapterError):
    """Raised when Analysis cannot safely interpret a retrieved representation."""


class RetrievedPayloadDecodeError(AnalysisNexusAdapterError):
    """Raised when a governed JSON representation cannot be decoded."""


@dataclass(frozen=True, slots=True)
class ResolvedInput:
    """Governed Analysis input resolved through the Research Nexus.

    Physical Nexus locators are deliberately excluded. Analysis receives semantic
    identity, governed metadata, verified content, and provenance only.
    """

    artifact_ref: ArtifactReference
    artifact_type: str
    schema_name: str
    schema_version: int
    payload: Mapping[str, Any]
    integrity_state: str
    provenance_summary: Mapping[str, Any]
    media_type: str
    content_hash: str

    def to_summary(self) -> dict[str, Any]:
        return {
            "artifact_ref": self.artifact_ref.to_dict(),
            "artifact_type": self.artifact_type,
            "schema_name": self.schema_name,
            "schema_version": self.schema_version,
            "integrity_state": self.integrity_state,
            "provenance_summary": dict(self.provenance_summary),
            "media_type": self.media_type,
            "content_hash": self.content_hash,
        }


class AnalysisNexusAdapter:
    """Analysis-facing adapter over the stable Research Nexus façade.

    The adapter does not know catalog tables, SQLite, payload directories,
    filesystem locators, Intake staging locations, or Warehouse paths.
    """

    def __init__(
        self,
        nexus: ResearchNexus,
        *,
        validator: SchemaValidator | None = None,
    ) -> None:
        self._nexus = nexus
        self._validator = validator or SchemaValidator()

    def resolve_artifact(
        self,
        artifact_ref: ArtifactReference,
        *,
        expected_artifact_types: Sequence[str] = (),
    ) -> ResolvedInput:
        # Nexus performs representation integrity verification before returning.
        retrieved = self._nexus.get(artifact_ref, verify=True)
        envelope = retrieved.envelope
        representation = retrieved.representation

        if expected_artifact_types and envelope.artifact_type not in set(expected_artifact_types):
            raise AnalysisNexusAdapterError(
                "Retrieved artifact type is not allowed for this Analysis input: "
                f"{envelope.artifact_type}; expected one of {tuple(expected_artifact_types)}"
            )

        media_type = representation.media_type.split(";", 1)[0].strip().lower()
        if media_type != "application/json":
            raise UnsupportedRepresentationError(
                f"Analysis Phase B supports governed JSON payloads only; got {representation.media_type!r}"
            )

        try:
            payload = json.loads(retrieved.payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RetrievedPayloadDecodeError(
                f"Could not decode governed JSON payload for "
                f"{artifact_ref.artifact_id}@{artifact_ref.artifact_version}"
            ) from exc

        if not isinstance(payload, dict):
            raise RetrievedPayloadDecodeError(
                "Governed Analysis input payload must decode to a JSON object"
            )

        # Structural meaning is validated from the envelope's governed schema.
        self._validator.validate(
            payload,
            schema_id=envelope.schema_id,
            schema_version=envelope.schema_version,
        )

        envelope_dict = envelope.to_dict()
        provenance = envelope_dict.get("provenance", {})
        if not isinstance(provenance, dict):
            provenance = {"value": provenance}

        return ResolvedInput(
            artifact_ref=envelope.reference(),
            artifact_type=envelope.artifact_type,
            schema_name=envelope.schema_id,
            schema_version=envelope.schema_version,
            payload=payload,
            integrity_state="VERIFIED",
            provenance_summary=provenance,
            media_type=representation.media_type,
            content_hash=representation.content_hash,
        )

    def resolve_artifacts(
        self,
        artifact_refs: Sequence[ArtifactReference],
        *,
        expected_artifact_types: Sequence[str] = (),
    ) -> tuple[ResolvedInput, ...]:
        return tuple(
            self.resolve_artifact(
                artifact_ref,
                expected_artifact_types=expected_artifact_types,
            )
            for artifact_ref in artifact_refs
        )

    def verify_artifact(self, artifact_ref: ArtifactReference) -> None:
        self._nexus.verify(artifact_ref)
