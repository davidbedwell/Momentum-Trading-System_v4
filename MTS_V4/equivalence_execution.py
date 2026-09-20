from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
from typing import Callable, Mapping, Sequence

from .batch_research_recording import BatchCampaignResearchRecorder
from .bootstrap import DEFAULT_MISSION, build_batch_runtime
from .contracts import ResearchPhase, SubjectMetadata
from .intake import IntakeEngine
from .live_sources import CompositeEvidenceSource, FinraWeeklyOffExchangeSource, YFinanceDailyOhlcvSource
from .openrouter_batch_provider import SubjectContextOpenRouterBatchResearchDirector
from .pre_sol_substrates import build_for_subject as build_pre_sol_substrates
from .participation_sources import YFinanceCatalystEventsSource, YFinanceIntradaySource, YFinanceMarketStructureSource
from .sec_share_structure_source import SecEdgarShareStructureSource
from .research_package_store import JsonResearchPackageStore
from .subject_scientific_context import SubjectContextSolBatchResearchDirector, load_subject_scientific_context
from .virgin_equivalence import (
    EquivalenceProtocolError,
    canonical_sha256,
    freeze_arm_manifest,
    freeze_starting_package,
    verify_identical_start,
    write_frozen_json,
)


def equivalence_market_source() -> CompositeEvidenceSource:
    """Frozen experiment evidence source: standard research inputs minus Unusual Whales.

    Unusual Whales was explicitly excluded from this experiment after the subscription
    expired. FINRA remains available symmetrically to both arms.
    """
    return CompositeEvidenceSource(
        YFinanceDailyOhlcvSource(),
        FinraWeeklyOffExchangeSource(),
        YFinanceMarketStructureSource(),
        YFinanceCatalystEventsSource(),
        YFinanceIntradaySource(),
        SecEdgarShareStructureSource(),
    )


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise EquivalenceProtocolError(f"required environment variable is not set: {name}")
    return value


def _artifact(path: Path) -> dict[str, object]:
    payload = path.read_bytes()
    return {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)}


def _jsonable(value: object) -> object:
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "value"):
        return value.value
    return str(value)


def prepare_identical_start(*, root: Path, ticker: str, experiment_root: Path) -> dict[str, object]:
    subject = SubjectMetadata(subject_id=f"equity:{ticker.upper()}", ticker=ticker.upper())
    context = load_subject_scientific_context(root, active_subject_id=subject.subject_id, include_same_subject_prior_science=False)
    runtime = build_batch_runtime(rd=None, mission=DEFAULT_MISSION, nexus_path=experiment_root / "_prepare_nexus.json", scientific_memory=context.memory_selection.store)
    evidence = IntakeEngine(runtime.cache).ingest(subject=subject, source=equivalence_market_source())
    precomputed = dict(build_pre_sol_substrates(subject=subject, evidence=evidence, cache=runtime.cache, analysis=runtime.analysis))
    package = freeze_starting_package(ticker.upper(), {
        "mission": DEFAULT_MISSION,
        "subject": _jsonable(subject),
        "evidence": _jsonable(evidence),
        "available_analysis_methods": [dict(item) for item in runtime.catalog.capability_payloads()],
        "starting_state": {
            "cross_subject_memory_source": str(context.memory_selection.source_path),
            "cross_subject_memory_sha256": canonical_sha256(context.prior_subject_science),
            "same_subject_prior_science": None,
            "precomputed_analysis_results": _jsonable(precomputed),
        },
    })
    write_frozen_json(experiment_root / ticker.upper() / "START.json", package)
    prepare_nexus = experiment_root / "_prepare_nexus.json"
    if prepare_nexus.exists():
        prepare_nexus.unlink()
    return package


def _run_arm(*, root: Path, ticker: str, arm_root: Path, start: Mapping[str, object], rd_factory: Callable):
    arm_root.mkdir(parents=True, exist_ok=False)
    subject = SubjectMetadata(subject_id=f"equity:{ticker.upper()}", ticker=ticker.upper())
    context = load_subject_scientific_context(root, active_subject_id=subject.subject_id, include_same_subject_prior_science=False)
    package_store = JsonResearchPackageStore(arm_root / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = rd_factory(package_store, context, subject)
    runtime = build_batch_runtime(rd=rd, mission=DEFAULT_MISSION, nexus_path=arm_root / "research_nexus.json", scientific_memory=context.memory_selection.store)
    evidence = IntakeEngine(runtime.cache).ingest(subject=subject, source=equivalence_market_source())
    precomputed = dict(build_pre_sol_substrates(subject=subject, evidence=evidence, cache=runtime.cache, analysis=runtime.analysis))
    live = freeze_starting_package(ticker.upper(), {
        "mission": DEFAULT_MISSION,
        "subject": _jsonable(subject),
        "evidence": _jsonable(evidence),
        "available_analysis_methods": [dict(item) for item in runtime.catalog.capability_payloads()],
        "starting_state": {
            "cross_subject_memory_source": str(context.memory_selection.source_path),
            "cross_subject_memory_sha256": canonical_sha256(context.prior_subject_science),
            "same_subject_prior_science": None,
            "precomputed_analysis_results": _jsonable(precomputed),
        },
    })
    verify_identical_start(start, live)
    decisions: list[object] = []
    reports: list[object] = []
    analyses: list[object] = []
    campaign_id = f"equivalence-{arm_root.name.lower()}-{ticker.lower()}"

    def accepted(request):
        recorder.record_accepted_request(campaign_id=campaign_id, subject=subject, request=request)

    def on_report(report, decision_count, analysis_count):
        recorder.record_report(report)
        reports.append(_jsonable(report))

    def on_decision(decision, decision_count, analysis_count):
        recorder.record_plan(campaign_id=campaign_id, subject=subject, decision=decision)
        recorder.record_predictive_hypothesis_updates(decision)
        recorder.record_closures(decision)
        decisions.append(_jsonable(decision))

    outcome = runtime.orchestrator.run(subject=subject, evidence=evidence, decision_callback=on_decision, report_callback=on_report, accepted_request_callback=accepted, precomputed_results=precomputed)
    analyses.extend(_jsonable(precomputed))
    write_frozen_json(arm_root / "decisions.json", {"decisions": decisions})
    write_frozen_json(arm_root / "reports.json", {"reports": reports})
    write_frozen_json(arm_root / "outcome.json", {"outcome": _jsonable(outcome), "precomputed_results": _jsonable(precomputed)})
    return rd, outcome


def run_direct_sol_arm(*, root: Path, ticker: str, experiment_root: Path, start: Mapping[str, object], sol_spend_usd: float):
    arm_root = experiment_root / ticker.upper() / "DIRECT_SOL"
    telemetry = arm_root / "sol_transport_telemetry.jsonl"
    old = os.environ.get("MTS_SOL_TELEMETRY_PATH")
    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(telemetry)
    try:
        def factory(store, context, subject):
            return SubjectContextSolBatchResearchDirector(research_package_store=store, prior_subject_scientific_context=context.prior_subject_science, same_subject_prior_scientific_context=None, revisit_change_context=None, base_url=_required_env("MTS_SOL_BASE_URL"), model=_required_env("MTS_SOL_MODEL"), api_key=_required_env("MTS_SOL_API_KEY"), timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")), required_subject_id=subject.subject_id, required_research_phase=ResearchPhase.EXPLORATION, sol_spend_limit_usd=sol_spend_usd, human_spend_authorization_callback=None)
        rd, outcome = _run_arm(root=root, ticker=ticker, arm_root=arm_root, start=start, rd_factory=factory)
    finally:
        if old is None: os.environ.pop("MTS_SOL_TELEMETRY_PATH", None)
        else: os.environ["MTS_SOL_TELEMETRY_PATH"] = old
    snapshot = rd.sol_spend_snapshot()
    usage = [asdict(snapshot)] if snapshot is not None else []
    artifacts = [_artifact(p) for p in sorted(arm_root.rglob("*.json"))]
    if telemetry.exists(): artifacts.append(_artifact(telemetry))
    manifest = freeze_arm_manifest(subject_id=ticker.upper(), arm="DIRECT_SOL", starting_sha256=str(start["sha256"]), artifacts=artifacts, usage=usage, complete=bool(outcome.closed))
    write_frozen_json(arm_root / "ARM_MANIFEST.json", manifest)
    return manifest


def run_gemini_rd_arm(*, root: Path, ticker: str, experiment_root: Path, start: Mapping[str, object], model: str, max_calls: int, max_spend_usd: float):
    arm_root = experiment_root / ticker.upper() / "GEMINI_RD"
    telemetry = arm_root / "openrouter_telemetry.jsonl"
    old = os.environ.get("MTS_OPENROUTER_RD_TELEMETRY_PATH")
    os.environ["MTS_OPENROUTER_RD_TELEMETRY_PATH"] = str(telemetry)
    try:
        def factory(store, context, subject):
            return SubjectContextOpenRouterBatchResearchDirector(research_package_store=store, prior_subject_scientific_context=context.prior_subject_science, same_subject_prior_scientific_context=None, revisit_change_context=None, base_url=os.getenv("MTS_OPENROUTER_BASE_URL", "https://openrouter.ai/api"), model=model, api_key=_required_env("MTS_OPENROUTER_API_KEY"), timeout_seconds=int(os.getenv("MTS_OPENROUTER_TIMEOUT_SECONDS", "600")), required_subject_id=subject.subject_id, required_research_phase=ResearchPhase.EXPLORATION, sol_spend_limit_usd=max_spend_usd, human_spend_authorization_callback=None, max_model_calls=max_calls, max_model_spend_usd=max_spend_usd)
        rd, outcome = _run_arm(root=root, ticker=ticker, arm_root=arm_root, start=start, rd_factory=factory)
    finally:
        if old is None: os.environ.pop("MTS_OPENROUTER_RD_TELEMETRY_PATH", None)
        else: os.environ["MTS_OPENROUTER_RD_TELEMETRY_PATH"] = old
    write_frozen_json(arm_root / "GEMINI_USAGE.json", dict(rd.openrouter_usage()))
    return arm_root, rd.openrouter_usage(), outcome
