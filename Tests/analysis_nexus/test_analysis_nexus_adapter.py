from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from Core.research_nexus import (
    ArtifactReference,
    Producer,
    Provenance,
    ResearchNexusConfig,
    build_research_nexus,
    create_artifact_envelope,
)
from Engines.Analysis.nexus_adapter import (
    AnalysisNexusAdapter,
    AnalysisNexusAdapterError,
)


def market_history_payload() -> dict:
    return {
        "symbol": "SMH",
        "timeframe": "1D",
        "semantic_fingerprint": "a" * 64,
        "materialization_policy": {
            "mode": "OBSERVATIONS_ONLY",
            "version": "phase-b-fixture-v1",
            "families": [],
            "measurement_names": [],
        },
        "observed_columns": ["date", "open", "high", "low", "close", "volume"],
        "measurement_columns": [],
        "records": [
            {
                "date": "2026-07-31T00:00:00Z",
                "open": 557.5,
                "high": 561.44,
                "low": 535.24,
                "close": 540.53,
                "volume": 14637100,
            }
        ],
        "quality_report": {"status": "PASSED"},
        "computation_audit": [],
    }


def publish_market_history(nexus, *, artifact_id: str = "artifact:phase-b-market"):
    payload = market_history_payload()
    envelope = create_artifact_envelope(
        artifact_type="NORMALIZED_DATASET",
        schema_id="mts.market-history",
        schema_version=1,
        producer=Producer(
            producer_type="ENGINE",
            producer_id="engine:intake",
        ),
        provenance=Provenance(
            software_version="intake-phase-b-fixture",
            method_id="method:intake-normalize-materialize",
            parameters={"source_id": "fixture:smh"},
        ),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        tags=("SMH", "1D", "market-history"),
        artifact_id=artifact_id,
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 18, 0, tzinfo=timezone.utc),
    )
    result = nexus.publish(
        envelope=envelope,
        payload=json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8"),
        media_type="application/json",
        index_fields={
            "artifact_type": "NORMALIZED_DATASET",
            "schema_id": "mts.market-history",
            "symbol": "SMH",
            "timeframe": "1D",
            "tags": ["SMH", "1D", "market-history"],
        },
    )
    return result.artifact_ref, payload


@pytest.fixture
def nexus(tmp_path: Path):
    return build_research_nexus(
        ResearchNexusConfig(runtime_root=tmp_path / "nexus")
    )


def test_resolves_verified_market_history_through_nexus(nexus):
    artifact_ref, expected_payload = publish_market_history(nexus)
    adapter = AnalysisNexusAdapter(nexus)

    resolved = adapter.resolve_artifact(
        artifact_ref,
        expected_artifact_types=("NORMALIZED_DATASET",),
    )

    assert resolved.artifact_ref == artifact_ref
    assert resolved.artifact_type == "NORMALIZED_DATASET"
    assert resolved.schema_name == "mts.market-history"
    assert resolved.schema_version == 1
    assert resolved.integrity_state == "VERIFIED"
    assert resolved.payload == expected_payload
    assert resolved.media_type == "application/json"
    assert resolved.content_hash.startswith("sha256:")
    assert len(resolved.content_hash.removeprefix("sha256:")) == 64


def test_resolved_input_does_not_expose_physical_nexus_locator(nexus):
    artifact_ref, _ = publish_market_history(nexus)
    resolved = AnalysisNexusAdapter(nexus).resolve_artifact(artifact_ref)

    summary = resolved.to_summary()
    rendered = repr(summary).lower()

    assert "locator" not in summary
    assert "payload_root" not in rendered
    assert "sqlite" not in rendered
    assert "file://" not in rendered
    assert "nexus-fs://" not in rendered


def test_adapter_rejects_unexpected_artifact_type(nexus):
    artifact_ref, _ = publish_market_history(nexus)

    with pytest.raises(AnalysisNexusAdapterError, match="not allowed"):
        AnalysisNexusAdapter(nexus).resolve_artifact(
            artifact_ref,
            expected_artifact_types=("FINDING",),
        )


def test_resolve_artifacts_preserves_requested_order(nexus):
    first, _ = publish_market_history(nexus, artifact_id="artifact:first")
    second, _ = publish_market_history(nexus, artifact_id="artifact:second")

    resolved = AnalysisNexusAdapter(nexus).resolve_artifacts((second, first))

    assert tuple(item.artifact_ref for item in resolved) == (second, first)


def test_verify_artifact_delegates_to_nexus_integrity_service(nexus):
    artifact_ref, _ = publish_market_history(nexus)
    adapter = AnalysisNexusAdapter(nexus)

    assert adapter.verify_artifact(artifact_ref) is None
