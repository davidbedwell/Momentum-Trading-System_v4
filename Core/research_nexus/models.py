from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping

from .identity import new_artifact_id
from .validation import SchemaValidator


def _timestamp(value: datetime) -> str:
    """Serialize an offset-aware datetime as RFC 3339-compatible ISO 8601."""
    if value.tzinfo is None or value.utcoffset() is None:
        # Do not silently assume UTC. A naive timestamp is semantically
        # ambiguous and must fail before it reaches the governed schema.
        raise ValueError("created_at must be offset-aware")

    text = value.isoformat()
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return text


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    artifact_id: str
    artifact_version: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_version": self.artifact_version,
        }


@dataclass(frozen=True, slots=True)
class GovernedReference:
    ref_type: str
    ref_id: str
    ref_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "ref_type": self.ref_type,
            "ref_id": self.ref_id,
        }
        if self.ref_version is not None:
            data["ref_version"] = self.ref_version
        return data


@dataclass(frozen=True, slots=True)
class Producer:
    producer_type: str
    producer_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "producer_type": self.producer_type,
            "producer_id": self.producer_id,
        }


@dataclass(frozen=True, slots=True)
class Provenance:
    input_refs: tuple[ArtifactReference, ...] = ()
    execution_ref: GovernedReference | None = None
    policy_refs: tuple[GovernedReference, ...] = ()
    configuration_refs: tuple[GovernedReference, ...] = ()
    software_version: str | None = None
    model_version: str | None = None
    method_id: str | None = None
    parameters: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "input_refs": [item.to_dict() for item in self.input_refs],
        }

        if self.execution_ref is not None:
            data["execution_ref"] = self.execution_ref.to_dict()
        if self.policy_refs:
            data["policy_refs"] = [item.to_dict() for item in self.policy_refs]
        if self.configuration_refs:
            data["configuration_refs"] = [
                item.to_dict() for item in self.configuration_refs
            ]
        if self.software_version is not None:
            data["software_version"] = self.software_version
        if self.model_version is not None:
            data["model_version"] = self.model_version
        if self.method_id is not None:
            data["method_id"] = self.method_id
        if self.parameters is not None:
            data["parameters"] = dict(self.parameters)

        return data


@dataclass(frozen=True, slots=True)
class ArtifactEnvelope:
    artifact_id: str
    artifact_version: int
    artifact_type: str
    schema_id: str
    schema_version: int
    created_at: datetime
    producer: Producer
    provenance: Provenance
    lifecycle_state: str
    persistence_class: str
    retention_class: str
    backup_requirement: str
    tags: tuple[str, ...] = ()

    def reference(self) -> ArtifactReference:
        return ArtifactReference(
            artifact_id=self.artifact_id,
            artifact_version=self.artifact_version,
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "artifact_id": self.artifact_id,
            "artifact_version": self.artifact_version,
            "artifact_type": self.artifact_type,
            "schema_id": self.schema_id,
            "schema_version": self.schema_version,
            "created_at": _timestamp(self.created_at),
            "producer": self.producer.to_dict(),
            "provenance": self.provenance.to_dict(),
            "lifecycle_state": self.lifecycle_state,
            "persistence_class": self.persistence_class,
            "retention_class": self.retention_class,
            "backup_requirement": self.backup_requirement,
        }
        if self.tags:
            data["tags"] = list(self.tags)
        return data

    def validate(self, validator: SchemaValidator | None = None) -> None:
        (validator or SchemaValidator()).validate(
            self.to_dict(),
            schema_id="mts.artifact-envelope",
            schema_version=1,
        )


def create_artifact_envelope(
    *,
    artifact_type: str,
    schema_id: str,
    schema_version: int,
    producer: Producer,
    provenance: Provenance,
    lifecycle_state: str,
    persistence_class: str,
    retention_class: str,
    backup_requirement: str,
    tags: tuple[str, ...] = (),
    artifact_id: str | None = None,
    artifact_version: int = 1,
    created_at: datetime | None = None,
    validator: SchemaValidator | None = None,
) -> ArtifactEnvelope:
    """Construct and validate a governed artifact envelope.

    Defaults are limited to identity, initial version, and current UTC time.
    Scientific/lifecycle/persistence semantics are never inferred.
    """
    envelope = ArtifactEnvelope(
        artifact_id=artifact_id or new_artifact_id(),
        artifact_version=artifact_version,
        artifact_type=artifact_type,
        schema_id=schema_id,
        schema_version=schema_version,
        created_at=created_at or datetime.now(timezone.utc),
        producer=producer,
        provenance=provenance,
        lifecycle_state=lifecycle_state,
        persistence_class=persistence_class,
        retention_class=retention_class,
        backup_requirement=backup_requirement,
        tags=tags,
    )
    envelope.validate(validator)
    return envelope
