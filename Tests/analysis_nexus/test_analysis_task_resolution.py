from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from Core.research_nexus import (
    ArtifactReference,
    Producer,
    Provenance,
    ResearchNexusConfig,
    build_research_nexus,
    create_artifact_envelope,
)
from Engines.Analysis import AnalysisTask
from Engines.Analysis.nexus_adapter import AnalysisNexusAdapter


def test_analysis_task_resolves_input_refs_without_source_path(tmp_path: Path):
    nexus = build_research_nexus(
        ResearchNexusConfig(runtime_root=tmp_path / "nexus")
    )

    payload = {
        "symbol": "SMH",
        "timeframe": "1D",
        "semantic_fingerprint": "b" * 64,
        "materialization_policy": {
            "mode": "OBSERVATIONS_ONLY",
            "version": "phase-b-task-fixture-v1",
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

    envelope = create_artifact_envelope(
        artifact_type="NORMALIZED_DATASET",
        schema_id="mts.market-history",
        schema_version=1,
        producer=Producer("ENGINE", "engine:intake"),
        provenance=Provenance(
            software_version="fixture",
            method_id="method:intake-normalize-materialize",
        ),
        lifecycle_state="DRAFT",
        persistence_class="CLASS_II",
        retention_class="SEMI_PERMANENT",
        backup_requirement="REQUIRED",
        artifact_id="artifact:task-input",
        artifact_version=1,
        created_at=datetime(2026, 8, 7, 18, 0, tzinfo=timezone.utc),
    )
    publication = nexus.publish(
        envelope=envelope,
        payload=json.dumps(payload, sort_keys=True, separators=(",", ":")).encode(),
        media_type="application/json",
        index_fields={"artifact_type": "NORMALIZED_DATASET", "symbol": "SMH"},
    )

    task = AnalysisTask(
        task_id="task:analysis:phase-b",
        task_version=1,
        research_plan_ref=ArtifactReference("artifact:plan", 1),
        question_ref=ArtifactReference("artifact:question", 1),
        input_artifact_refs=(publication.artifact_ref,),
        requested_objective="Resolve governed market history for Analysis.",
    )

    resolved = AnalysisNexusAdapter(nexus).resolve_artifacts(
        task.input_artifact_refs,
        expected_artifact_types=("NORMALIZED_DATASET",),
    )

    assert len(resolved) == 1
    assert resolved[0].payload["symbol"] == "SMH"
    assert publication.artifact_ref == resolved[0].artifact_ref
    assert "/Users/" not in repr(resolved[0].to_summary())
    assert ".parquet" not in repr(resolved[0].to_summary())
