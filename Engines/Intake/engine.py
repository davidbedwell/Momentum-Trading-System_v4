
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from Core.deterministic_computation import build_registry, execute_computations

from .adapters.base import SourceAdapter
from .identity import dataframe_sha256, semantic_version_fingerprint
from .models import IntakeArtifact, IntakeRequest, IntakeResult, MaterializationMode
from .normalize import normalize_ohlcv
from .publisher import NexusPublisher, PublicationNotConfigured
from .quality import validate_and_profile_ohlcv

ENGINE_ID = "INTAKE"
ENGINE_VERSION = "0.1.0"
SCHEMA_ID = "mts.market-history"
SCHEMA_VERSION = 1


class IntakeEngine:
    def __init__(self, publisher: NexusPublisher | None = None) -> None:
        self.publisher = publisher

    def process(self, adapter: SourceAdapter, request: IntakeRequest) -> IntakeArtifact:
        source = adapter.load()
        normalized = normalize_ohlcv(source.frame)
        quality = validate_and_profile_ohlcv(normalized)
        observed_hash = dataframe_sha256(normalized)

        measured, execution_audit, measurement_columns = self._materialize(
            normalized, request
        )

        registry = build_registry()
        family_ids = execution_audit.get(
            "family_id", pd.Series(dtype=str)
        ).tolist()
        formula_versions = {
            family_id: registry[family_id].version
            for family_id in family_ids
            if family_id in registry
        }

        policy_payload = {
            "mode": request.policy.mode.value,
            "version": request.policy.version,
            "families": list(request.policy.families),
            "measurement_names": list(request.policy.measurement_names),
        }
        fingerprint_inputs = {
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "symbol": request.symbol.upper(),
            "timeframe": request.timeframe,
            "source_id": source.source_id,
            "observed_sha256": observed_hash,
            "materialization_policy": policy_payload,
            "formula_versions": formula_versions,
            "engine_version": ENGINE_VERSION,
        }
        fingerprint = semantic_version_fingerprint(fingerprint_inputs)

        provenance = {
            "producer_engine": ENGINE_ID,
            "producer_version": ENGINE_VERSION,
            "source_id": source.source_id,
            "source_format": source.source_format,
            "source_locator": source.source_locator,
            "provider_metadata": dict(source.provider_metadata),
            "observed_sha256": observed_hash,
            "observed_columns": ["date","open","high","low","close","volume"],
            "derived_columns": list(measurement_columns),
            "formula_versions": formula_versions,
            "materialization_policy_version": request.policy.version,
            "temporal_classification": {
                "observations": "OBSERVED",
                "measurements": "DERIVED_CONTEMPORANEOUS",
            },
        }

        manifest = {
            "schema_id": SCHEMA_ID,
            "schema_version": SCHEMA_VERSION,
            "semantic_fingerprint": fingerprint,
            "symbol": request.symbol.upper(),
            "timeframe": request.timeframe,
            "row_count": int(len(measured)),
            "observation_column_count": 6,
            "measurement_count": len(measurement_columns),
            "materialization_mode": request.policy.mode.value,
            "materialization_policy_version": request.policy.version,
            "requested_by": request.requested_by,
            "correlation_id": request.correlation_id,
            "execution_completed_at_utc": datetime.now(timezone.utc).isoformat(),
            "semantic_fingerprint_inputs": fingerprint_inputs,
        }

        return IntakeArtifact(
            semantic_fingerprint=fingerprint,
            schema_id=SCHEMA_ID,
            schema_version=SCHEMA_VERSION,
            engine_version=ENGINE_VERSION,
            symbol=request.symbol.upper(),
            timeframe=request.timeframe,
            observations=measured,
            measurement_columns=measurement_columns,
            materialization_policy=policy_payload,
            provenance=provenance,
            quality_report=quality,
            execution_audit=execution_audit,
            manifest=manifest,
        )

    def publish(self, artifact: IntakeArtifact) -> object:
        if self.publisher is None:
            raise PublicationNotConfigured(
                "Research Nexus publisher is not configured; Intake will not "
                "write durable state outside the Nexus."
            )
        return self.publisher.publish_intake_artifact(artifact)

    def run(
        self,
        adapter: SourceAdapter,
        request: IntakeRequest,
        *,
        publish: bool = True,
    ) -> IntakeResult:
        artifact = self.process(adapter, request)
        reference = self.publish(artifact) if publish else None
        return IntakeResult(artifact=artifact, nexus_reference=reference)

    def _materialize(
        self,
        normalized: pd.DataFrame,
        request: IntakeRequest,
    ) -> tuple[pd.DataFrame, pd.DataFrame, tuple[str, ...]]:
        policy = request.policy
        if policy.mode == MaterializationMode.OBSERVATIONS_ONLY:
            return normalized.copy(), pd.DataFrame(columns=[
                "family_id","formula_version","status","measurements_added",
                "elapsed_seconds","provenance"
            ]), ()

        before = set(normalized.columns)
        if policy.mode == MaterializationMode.EXPLICIT_MEASUREMENTS:
            result = execute_computations(
                normalized,
                measurement_names=list(policy.measurement_names),
            )
        elif policy.families:
            result = execute_computations(
                normalized,
                families=list(policy.families),
            )
        else:
            result = execute_computations(normalized)

        measurement_columns = tuple(
            c for c in result.data.columns if c not in before
        )
        return result.data, result.audit, measurement_columns
