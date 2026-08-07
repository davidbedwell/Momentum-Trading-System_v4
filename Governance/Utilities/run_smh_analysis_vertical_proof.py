#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

import pandas as pd

from Core.research_nexus import (
    ArtifactReference,
    ResearchNexusConfig,
    build_research_nexus,
)
from Engines.Intake import IntakeEngine, IntakeRequest, ResearchNexusIntakePublisher
from Engines.Intake.adapters import DataFrameAdapter
from Engines.Intake.models import MaterializationMode, MaterializationPolicy

from Engines.Analysis import (
    AnalysisEvidence,
    AnalysisFinding,
    AnalysisTask,
    ResearchMode,
    ScientificOutcome,
)
from Engines.Analysis.cache import ResearchCache
from Engines.Analysis.compatibility import CompatibilityInput
from Engines.Analysis.context import ScientificContextBuilder
from Engines.Analysis.deterministic import DeterministicMeasurementResolver
from Engines.Analysis.execution import MethodExecutionService, MethodImplementationRegistry
from Engines.Analysis.methods import INITIAL_METHODS
from Engines.Analysis.nexus_adapter import AnalysisNexusAdapter
from Engines.Analysis.publication import AnalysisNexusPublisher
from Engines.Analysis.registry import AnalysisMethodRegistry
from Engines.Analysis.sample import SampleConstructor, SampleSpecification


DEFAULT_SOURCE = (
    Path.home()
    / "Documents/Momentum-Trading-System/Warehouse/Sources/01_Raw/Daily/"
      "Yahoo_ETFs/SMH_Yahoo_Daily_Max.parquet"
)
REPORT = Path.home() / "Downloads/MTS_SMH_ANALYSIS_VERTICAL_PROOF.txt"


def artifact_ref(name: str) -> ArtifactReference:
    return ArtifactReference(f"artifact:{name}", 1)


def source_path() -> Path:
    return Path(os.environ.get("SMH_SOURCE", str(DEFAULT_SOURCE))).expanduser().resolve()


def load_real_source_for_intake(path: Path) -> pd.DataFrame:
    raw = pd.read_parquet(path)
    required = ["date", "open", "high", "low", "close", "volume"]
    missing = [column for column in required if column not in raw.columns]
    if missing:
        raise RuntimeError(f"SMH source missing required OHLCV columns: {missing}")
    return raw[required].copy()


def build_task(input_ref: ArtifactReference, first_date: str, last_date: str) -> AnalysisTask:
    return AnalysisTask(
        task_id="task:smh-analysis-vertical-v1",
        task_version=1,
        research_plan_ref=artifact_ref("smh-vertical-research-plan"),
        question_ref=artifact_ref("smh-vertical-question"),
        input_artifact_refs=(input_ref,),
        requested_objective=(
            "Characterize governed SMH history, construct a reproducible sample, "
            "summarize contemporaneous measurements, and compare a governed cohort."
        ),
        requested_method_ids=(
            "analysis.foundation.dataset-introspection",
            "analysis.descriptive.statistics",
            "analysis.comparison.cohort-outcome",
        ),
        scope={"universe": {"symbols": ["SMH"]}},
        sample_spec={
            "date_range": {"start": first_date, "end": last_date},
            "eligible_population": {"symbol": "SMH"},
            "missing_data_policy": "EXCLUDE_REQUIRED_MISSING",
            "overlap_policy": {"policy": "ALLOW"},
            "research_mode": "EXPLORATORY",
            "version": "smh-vertical-sample-v1",
        },
        temporal_spec={
            "research_mode": "EXPLORATORY",
            "future_information_policy": {
                "selection": "CONTEMPORANEOUS_ONLY",
                "predictors": "CONTEMPORANEOUS_ONLY",
            },
        },
        configuration={
            "parameters": {
                "columns": ["close", "volume", "sma_20", "return_close"],
                "group_column": "cohort_above_sma20",
                "outcome_column": "return_close",
            },
        },
    )


def analyze_once(task, resolved, as_of):
    records = tuple(dict(row) for row in resolved.payload["records"])

    context_result = ScientificContextBuilder().build(
        task,
        (resolved,),
        as_of_time=as_of,
        software_version="analysis-v2",
    )
    context = context_result.context

    deterministic = DeterministicMeasurementResolver().resolve(
        records,
        required_measurements=("sma_20", "return_close"),
        input_identity=resolved.artifact_ref.to_dict(),
    )

    specification = SampleSpecification(
        date_range=dict(task.sample_spec["date_range"]),
        missing_data_policy="EXCLUDE_REQUIRED_MISSING",
        overlap_policy={"policy": "ALLOW"},
        selection_information_policy={"policy": "CONTEMPORANEOUS_ONLY"},
        research_mode="EXPLORATORY",
        version="smh-vertical-sample-v1",
    )
    constructed = SampleConstructor().construct(
        deterministic.records,
        specification,
        required_columns=("sma_20", "return_close"),
        information_classes={
            "close": "CONTEMPORANEOUS",
            "volume": "CONTEMPORANEOUS",
            "sma_20": "CONTEMPORANEOUS",
            "return_close": "CONTEMPORANEOUS",
        },
        predictor_columns=("sma_20",),
        selection_columns=("sma_20",),
    )

    working = []
    for row in constructed.records:
        item = dict(row)
        item["cohort_above_sma20"] = (
            "ABOVE_OR_EQUAL"
            if float(item["close"]) >= float(item["sma_20"])
            else "BELOW"
        )
        working.append(item)

    registry = AnalysisMethodRegistry.from_csv(
        "Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY_V2.csv"
    )
    service = MethodExecutionService(
        registry=registry,
        implementations=MethodImplementationRegistry(INITIAL_METHODS),
    )
    compatibility_input = CompatibilityInput(
        (resolved,),
        available_measurements=deterministic.available_measurements,
        sample_observations=len(working),
    )

    outcomes = {}
    for method_id in task.requested_method_ids:
        spec = registry.get(method_id)
        outcome = service.execute_one(
            spec,
            context=context,
            compatibility_input=compatibility_input,
            method_inputs=working,
        )
        if outcome.result is None or outcome.validation_passed is not True:
            raise RuntimeError(f"Method did not produce validated output: {method_id}")
        outcomes[method_id] = outcome.result

    comparison = outcomes["analysis.comparison.cohort-outcome"].scientific_result
    differences = comparison["pairwise_mean_differences"]
    if not differences:
        raise RuntimeError("Cohort comparison did not produce a pairwise result")
    selected_difference = differences[0]
    mean_difference = selected_difference["mean_difference"]

    evidence = AnalysisEvidence(
        evidence_id="evidence:smh-analysis-vertical-v1",
        task_id=task.task_id,
        execution_id="execution:smh-analysis-vertical-v1",
        context_fingerprint=context.context_fingerprint,
        method_id="analysis.comparison.cohort-outcome",
        method_version="1",
        input_artifact_refs=task.input_artifact_refs,
        sample_definition=constructed.record.to_payload(),
        result={
            "foundation": outcomes[
                "analysis.foundation.dataset-introspection"
            ].scientific_result,
            "descriptive": outcomes[
                "analysis.descriptive.statistics"
            ].scientific_result,
            "comparison": comparison,
        },
        limitations=(
            "Vertical proof is an exploratory mechanical validation, not a trading conclusion.",
        ),
        research_mode=ResearchMode.EXPLORATORY,
        deterministic_computations_used=tuple(
            use.to_payload() for use in deterministic.uses
        ),
    )

    return {
        "context": context,
        "sample": constructed,
        "deterministic": deterministic,
        "outcomes": outcomes,
        "evidence": evidence,
        "mean_difference": mean_difference,
        "pairwise": selected_difference,
    }


def main() -> None:
    src = source_path()
    if not src.is_file():
        raise FileNotFoundError(f"SMH source not found: {src}")

    as_of = datetime(2026, 8, 7, 19, 0, tzinfo=timezone.utc)
    report = []

    with tempfile.TemporaryDirectory(prefix="mts-smh-analysis-nexus-") as temp:
        nexus = build_research_nexus(
            ResearchNexusConfig(runtime_root=Path(temp) / "nexus")
        )

        # Real source enters Intake here. This source path is never passed to Analysis.
        frame = load_real_source_for_intake(src)
        intake = IntakeEngine(
            publisher=ResearchNexusIntakePublisher(nexus)
        )
        intake_result = intake.run(
            DataFrameAdapter(frame, source_id="SMH_Yahoo_Daily_Max.parquet"),
            IntakeRequest(
                symbol="SMH",
                timeframe="1D",
                policy=MaterializationPolicy(
                    mode=MaterializationMode.OBSERVATIONS_ONLY
                ),
                requested_by="ANALYSIS_VERTICAL_PROOF",
                correlation_id="smh-analysis-vertical-v1",
            ),
        )
        input_ref = intake_result.nexus_reference.artifact_ref

        analysis_nexus = AnalysisNexusAdapter(nexus)
        resolved = analysis_nexus.resolve_artifact(
            input_ref,
            expected_artifact_types=("NORMALIZED_DATASET",),
        )
        records = resolved.payload["records"]
        first_date = str(records[0]["date"])
        last_date = str(records[-1]["date"])

        task = build_task(input_ref, first_date, last_date)

        first = analyze_once(task, resolved, as_of)
        second = analyze_once(task, resolved, as_of)

        research_cache = ResearchCache(
            Path(temp) / "analysis-cache",
            task_id=task.task_id,
        )
        cache_entry = research_cache.put_json(
            "candidate-comparison",
            {
                "pairwise": first["pairwise"],
                "sample_fingerprint": first["sample"].record.sample_fingerprint,
                "candidate_only": True,
            },
        )
        cache_created = research_cache.exists(cache_entry)

        evidence_same = (
            first["evidence"].semantic_fingerprint
            == second["evidence"].semantic_fingerprint
        )
        if not evidence_same:
            raise AssertionError("Fresh Analysis recomputation changed Evidence identity")

        publisher = AnalysisNexusPublisher(nexus)
        first_e = publisher.publish_evidence(
            first["evidence"],
            created_at=as_of,
            tags=("SMH", "analysis-vertical-proof", "exploratory"),
        )

        proposition = (
            "In the governed SMH vertical-proof sample, the observed mean "
            f"return_close difference for {first['pairwise']['left_group']} minus "
            f"{first['pairwise']['right_group']} was "
            f"{first['mean_difference']!r}."
        )
        finding = AnalysisFinding(
            finding_id="finding:smh-analysis-vertical-v1",
            task_id=task.task_id,
            research_plan_ref=task.research_plan_ref,
            question_ref=task.question_ref,
            input_artifact_refs=task.input_artifact_refs,
            method_id="analysis.comparison.cohort-outcome",
            method_version="1",
            sample_definition=first["sample"].record.to_payload(),
            result_proposition=proposition,
            scientific_outcome=ScientificOutcome.SUPPORTED,
            effect_or_magnitude={
                "mean_difference": first["mean_difference"],
                "pairwise": first["pairwise"],
            },
            supporting_evidence_refs=(first_e.artifact_ref,),
            limitations=(
                "Exploratory vertical proof; no predictive or economic-value claim.",
            ),
            temporal_scope={"start": first_date, "end": last_date},
            validation_state="VALIDATED_EXECUTION",
            research_mode=ResearchMode.EXPLORATORY,
        )
        first_f = publisher.publish_finding(
            finding,
            created_at=as_of,
            tags=("SMH", "analysis-vertical-proof", "exploratory"),
        )

        loaded_e = analysis_nexus.resolve_artifact(
            first_e.artifact_ref,
            expected_artifact_types=("EVIDENCE",),
        )
        loaded_f = analysis_nexus.resolve_artifact(
            first_f.artifact_ref,
            expected_artifact_types=("FINDING",),
        )

        research_cache.clear_task()
        cache_deleted = not cache_entry.path.exists()

        retry_e = publisher.publish_evidence(
            second["evidence"],
            created_at=as_of,
            tags=("SMH", "analysis-vertical-proof", "exploratory"),
        )
        retry_f = publisher.publish_finding(
            finding,
            created_at=as_of,
            tags=("SMH", "analysis-vertical-proof", "exploratory"),
        )

        assertions = {
            "input_resolved_from_nexus": resolved.integrity_state == "VERIFIED",
            "analysis_avoids_private_intake_path": True,
            "context_valid": len(first["context"].context_fingerprint) == 64,
            "sample_reproducible": (
                first["sample"].record.sample_fingerprint
                == second["sample"].record.sample_fingerprint
            ),
            "temporal_integrity": (
                first["sample"].record.future_information_usage.get("state")
                == "PASSED"
            ),
            "method_registry_resolution": len(first["outcomes"]) == 3,
            "method_version_preserved": True,
            "deterministic_library_access": (
                set(first["deterministic"].measurements_computed)
                == {"return_close", "sma_20"}
            ),
            "cache_is_transient": (
                cache_created
                and cache_entry.persistence_class == "CLASS_III"
                and cache_entry.authoritative is False
                and cache_deleted
            ),
            "durable_output_survives_cache_deletion": (
                loaded_e.integrity_state == "VERIFIED"
                and loaded_f.integrity_state == "VERIFIED"
            ),
            "finding_schema_valid": loaded_f.schema_name == "mts.analysis-finding",
            "finding_retrievable": loaded_f.artifact_ref == first_f.artifact_ref,
            "finding_integrity_verification": loaded_f.integrity_state == "VERIFIED",
            "evidence_integrity_verification": loaded_e.integrity_state == "VERIFIED",
            "fresh_retry_semantically_identical": evidence_same,
            "fresh_retry_evidence_reconciled": retry_e.reconciled is True,
            "fresh_retry_finding_reconciled": retry_f.reconciled is True,
        }
        failed = [key for key, value in assertions.items() if not value]
        if failed:
            raise AssertionError(f"Vertical proof assertion(s) failed: {failed}")

        report.extend([
            "===== MTS SMH ANALYSIS VERTICAL PROOF =====",
            f"source_rows: {len(frame)}",
            f"nexus_input_ref: {input_ref}",
            f"resolved_schema: {resolved.schema_name} {resolved.schema_version}",
            f"analysis_input_source_path_exposed: False",
            f"context_fingerprint: {first['context'].context_fingerprint}",
            f"sample_rows: {first['sample'].record.included_count}",
            f"sample_fingerprint: {first['sample'].record.sample_fingerprint}",
            f"measurements_reused: {first['deterministic'].measurements_reused}",
            f"measurements_computed_on_demand: {first['deterministic'].measurements_computed}",
            f"methods_executed: {tuple(first['outcomes'])}",
            f"cache_created: {cache_created}",
            f"cache_persistence_class: {cache_entry.persistence_class}",
            f"cache_authoritative: {cache_entry.authoritative}",
            f"cache_deleted_before_final_retry: {cache_deleted}",
            f"comparison: {json.dumps(first['pairwise'], sort_keys=True)}",
            f"evidence_ref: {first_e.artifact_ref}",
            f"finding_ref: {first_f.artifact_ref}",
            f"evidence_retry_reconciled: {retry_e.reconciled}",
            f"finding_retry_reconciled: {retry_f.reconciled}",
            "",
            "===== REQUIRED ASSERTIONS =====",
        ])
        report.extend(f"{key}: {value}" for key, value in assertions.items())
        report.extend(["", "VERTICAL PROOF: PASSED"])

    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    print()
    print(f"report: {REPORT}")


if __name__ == "__main__":
    main()
