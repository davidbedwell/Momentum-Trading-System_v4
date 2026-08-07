from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

import numpy as np
import pandas as pd

from Core.research_nexus import (
    ArtifactNotFoundError,
    ArtifactReference,
    Producer,
    Provenance,
    ResearchNexus,
    SchemaValidator,
    create_artifact_envelope,
)

from .models import IntakeArtifact

PAYLOAD_SCHEMA_ID = "mts.market-history"
PAYLOAD_SCHEMA_VERSION = 1
PRODUCER_ID = "engine:intake"


def _json_scalar(value: Any) -> Any:
    if value is None or value is pd.NA:
        return None
    if isinstance(value, (np.floating, float)):
        if pd.isna(value):
            return None
        return float(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, pd.Timestamp):
        return value.isoformat().replace("+00:00", "Z")
    return value


def market_history_payload(artifact: IntakeArtifact) -> dict[str, Any]:
    records = [
        {str(k): _json_scalar(v) for k, v in row.items()}
        for row in artifact.observations.to_dict(orient="records")
    ]
    # Runtime telemetry is deliberately excluded from canonical scientific
    # content. Recomputing identical source data must reproduce identical
    # immutable payload bytes.
    non_semantic_audit_fields = {"elapsed_seconds"}

    audit = [
        {
            str(k): _json_scalar(v)
            for k, v in row.items()
            if k not in non_semantic_audit_fields
        }
        for row in artifact.execution_audit.to_dict(orient="records")
    ]
    return {
        "symbol": artifact.symbol,
        "timeframe": artifact.timeframe,
        "semantic_fingerprint": artifact.semantic_fingerprint,
        "materialization_policy": dict(artifact.materialization_policy),
        "observed_columns": ["date", "open", "high", "low", "close", "volume"],
        "measurement_columns": list(artifact.measurement_columns),
        "records": records,
        "quality_report": dict(artifact.quality_report),
        "computation_audit": audit,
    }


def canonical_payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def deterministic_artifact_id(semantic_fingerprint: str) -> str:
    digest = hashlib.sha256(
        f"mts.market-history|{semantic_fingerprint}".encode("utf-8")
    ).hexdigest()
    return f"artifact:{digest[:32]}"


def _artifact_type_from_governance(validator: SchemaValidator) -> str:
    governed = validator.registry.get("mts.controlled-vocabularies", 1)
    defs = governed.document.get("$defs", {})
    allowed = tuple(defs.get("artifact_type", {}).get("enum", ()))
    preferred = (
        "NORMALIZED_DATASET",
        "DATASET",
        "MARKET_DATASET",
        "OBSERVATION_SET",
        "OBSERVATION",
        "MEASUREMENT_SET",
    )
    for candidate in preferred:
        if candidate in allowed:
            return candidate
    raise RuntimeError(
        "Governed artifact_type vocabulary has no dataset/observation type "
        f"suitable for Intake market history. Available values: {allowed}"
    )


class ResearchNexusIntakePublisher:
    """Translate Intake output into the public Research Nexus contract only."""

    def __init__(
        self,
        nexus: ResearchNexus,
        *,
        validator: SchemaValidator | None = None,
        artifact_type: str | None = None,
    ) -> None:
        self.nexus = nexus
        self.validator = validator or SchemaValidator()
        self.artifact_type = artifact_type or _artifact_type_from_governance(
            self.validator
        )

    def _canonical_created_at(self, ref: ArtifactReference) -> datetime:
        """Reuse the canonical timestamp when retrying an existing identity.

        A retry must reproduce the existing immutable envelope rather than
        generating a new timestamp. On first publication, current UTC is valid.
        """
        try:
            existing = self.nexus.get(ref)
        except ArtifactNotFoundError:
            return datetime.now(timezone.utc)
        return existing.envelope.created_at

    def publish_intake_artifact(self, artifact: IntakeArtifact):
        payload = market_history_payload(artifact)
        self.validator.validate(
            payload,
            schema_id=PAYLOAD_SCHEMA_ID,
            schema_version=PAYLOAD_SCHEMA_VERSION,
        )
        payload_bytes = canonical_payload_bytes(payload)

        artifact_id = deterministic_artifact_id(artifact.semantic_fingerprint)
        artifact_ref = ArtifactReference(artifact_id, 1)
        created_at = self._canonical_created_at(artifact_ref)

        envelope = create_artifact_envelope(
            artifact_type=self.artifact_type,
            schema_id=PAYLOAD_SCHEMA_ID,
            schema_version=PAYLOAD_SCHEMA_VERSION,
            producer=Producer(
                producer_type="ENGINE",
                producer_id=PRODUCER_ID,
            ),
            provenance=Provenance(
                software_version=artifact.engine_version,
                method_id="method:intake-normalize-materialize",
                parameters={
                    "semantic_fingerprint": artifact.semantic_fingerprint,
                    "source_id": artifact.provenance.get("source_id"),
                    "source_format": artifact.provenance.get("source_format"),
                    "observed_sha256": artifact.provenance.get("observed_sha256"),
                    "formula_versions": artifact.provenance.get(
                        "formula_versions", {}
                    ),
                    "materialization_policy": dict(
                        artifact.materialization_policy
                    ),
                },
            ),
            lifecycle_state="DRAFT",
            persistence_class="CLASS_II",
            retention_class="SEMI_PERMANENT",
            backup_requirement="REQUIRED",
            tags=(artifact.symbol, artifact.timeframe, "market-history"),
            artifact_id=artifact_id,
            artifact_version=1,
            created_at=created_at,
        )

        result = self.nexus.publish(
            envelope=envelope,
            payload=payload_bytes,
            media_type="application/json",
            index_fields={
                "artifact_type": self.artifact_type,
                "schema_id": PAYLOAD_SCHEMA_ID,
                "symbol": artifact.symbol,
                "timeframe": artifact.timeframe,
                "tags": [artifact.symbol, artifact.timeframe, "market-history"],
            },
        )
        self.nexus.verify(result.artifact_ref)
        return result
