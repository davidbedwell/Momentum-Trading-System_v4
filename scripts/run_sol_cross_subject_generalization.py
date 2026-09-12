from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Mapping, Sequence

from MTS_V4.batch_contracts import BatchExecutionReport
from MTS_V4.batch_research_recording import BatchCampaignResearchRecorder
from MTS_V4.bootstrap import DEFAULT_MISSION, build_batch_runtime
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.cross_subject_generalization import (
    GENERALIZATION_SUBJECT_ID,
    SolCrossSubjectGeneralizationResearchDirector,
    generalization_evidence_view,
)
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
    SolSpendAuthorizationSnapshot,
)


# Known earlier v4 subjects that may live outside the currently discoverable
# state-directory layout. Discovery below adds every additional subject actually
# present in durable Nexus/package artifacts, so this tuple is a floor, not a cap.
DEFAULT_PREVIOUSLY_ANALYZED_TICKERS = (
    "AAPL", "MSFT", "XOM", "AMD", "AMZN", "BA", "GOOGL", "JPM", "META", "NVDA", "TSLA"
)

GENERALIZATION_MISSION = DEFAULT_MISSION + (
    " This campaign operates at the cross-subject level. Determine whether accumulated ticker-specific scientific "
    "experience supports any falsifiable relationship that transfers, generalizes, reverses, or becomes conditional "
    "across subjects. Direct multi-ticker Analysis is permitted during EXPLORATION when Sol judges it useful."
)


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def _append_jsonl(path: Path, payload: object) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True, default=str, separators=(",", ":")) + "\n")


def _format_money(value: float | None) -> str:
    return "unknown" if value is None else f"${value:.2f}"


def _interactive_spend_authorization(snapshot: SolSpendAuthorizationSnapshot) -> float | None:
    print("\nHUMAN SOL SPEND AUTHORIZATION REQUIRED", flush=True)
    print(f"AUTHORIZED={_format_money(snapshot.authorized_spend_usd)}", flush=True)
    print(f"ACTUAL_SPEND={_format_money(snapshot.actual_spend_usd)}", flush=True)
    print(f"SOL_CALLS_COMPLETED={snapshot.completed_sol_calls}", flush=True)
    print(f"ESTIMATED_PERCENT_COMPLETE={snapshot.estimated_percent_complete}", flush=True)
    print(f"ESTIMATED_REMAINING_BATCHES={snapshot.estimated_remaining_batches}", flush=True)
    print(f"ESTIMATED_REMAINING_SOL_CALLS={snapshot.estimated_remaining_sol_calls}", flush=True)
    try:
        raw = input("Enter a new total Sol spend ceiling in USD, or press Enter to stop: ").strip()
    except EOFError:
        return None
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        print("Authorization was not numeric; stopping.", flush=True)
        return None
    if value <= snapshot.authorized_spend_usd:
        print("New authorization must exceed the current ceiling; stopping.", flush=True)
        return None
    return value


def _ticker_from_subject_id(subject_id: object) -> str | None:
    if not isinstance(subject_id, str) or not subject_id.startswith("equity:"):
        return None
    ticker = subject_id.split(":", 1)[1].strip().upper()
    return ticker or None


def _collect_subject_ids(value: object, output: set[str]) -> None:
    if isinstance(value, Mapping):
        subject_id = value.get("subject_id")
        if isinstance(subject_id, str) and subject_id.startswith("equity:"):
            output.add(subject_id)
        for child in value.values():
            _collect_subject_ids(child, output)
    elif isinstance(value, list):
        for child in value:
            _collect_subject_ids(child, output)


def _discover_tickers(root: Path) -> tuple[str, ...]:
    tickers = set(DEFAULT_PREVIOUSLY_ANALYZED_TICKERS)

    configured = os.getenv("MTS_GENERALIZATION_PREVIOUSLY_ANALYZED_TICKERS", "").strip()
    if configured:
        tickers.update(item.strip().upper() for item in configured.split(",") if item.strip())

    # Subject directories are the strongest cheap signal that a ticker actually ran.
    for nexus_path in root.glob("mts-v4-*/subjects/*/research_nexus.json"):
        tickers.add(nexus_path.parent.name.upper())

    # Also inspect every durable v4 Nexus recursively. This catches one-subject,
    # recovered, revisit, and future runner layouts without hard-coding names.
    discovered_subject_ids: set[str] = set()
    for nexus_path in root.glob("mts-v4-*/**/research_nexus.json"):
        try:
            raw = json.loads(nexus_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        _collect_subject_ids(raw, discovered_subject_ids)
    for subject_id in discovered_subject_ids:
        ticker = _ticker_from_subject_id(subject_id)
        if ticker:
            tickers.add(ticker)

    return tuple(sorted(ticker for ticker in tickers if ticker))


def _compact_package(
    package: Mapping[str, object],
    source_path: Path,
    *,
    source_format: object = None,
) -> Mapping[str, object] | None:
    subject_id = package.get("subject_id")
    ticker = _ticker_from_subject_id(subject_id)
    if ticker is None:
        return None
    hypotheses = package.get("hypotheses", [])
    findings = package.get("findings", [])
    predictive_hypotheses = package.get("predictive_hypotheses", [])
    unresolved_issues = package.get("unresolved_issues", [])
    analyses = package.get("analyses", [])
    return {
        "source_path": str(source_path),
        "source_format": source_format,
        "subject_id": subject_id,
        "ticker": ticker,
        "rp_id": package.get("rp_id"),
        "campaign_id": package.get("campaign_id"),
        "parent_rp_id": package.get("parent_rp_id"),
        "status": package.get("status"),
        "objective": package.get("objective"),
        "originating_question": package.get("originating_question"),
        "originating_rationale": package.get("originating_rationale"),
        "close_reason": package.get("close_reason"),
        "final_assessment": package.get("final_assessment"),
        "hypotheses": hypotheses if isinstance(hypotheses, list) else [],
        "findings": findings if isinstance(findings, list) else [],
        "predictive_hypotheses": predictive_hypotheses if isinstance(predictive_hypotheses, list) else [],
        "unresolved_issues": unresolved_issues if isinstance(unresolved_issues, list) else [],
        "analysis_lineage": analyses if isinstance(analyses, list) else [],
    }


def _historical_subject_context(root: Path, tickers: Sequence[str]) -> Mapping[str, object]:
    wanted = set(tickers)
    packages_by_ticker: dict[str, list[Mapping[str, object]]] = {ticker: [] for ticker in tickers}
    seen_fingerprints: set[str] = set()
    for package_path in root.glob("mts-v4-*/**/research_packages/*.json"):
        try:
            raw = json.loads(package_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, Mapping):
            continue

        source_format = raw.get("format")
        package: Mapping[str, object] = raw
        if source_format == JsonResearchPackageStore.FORMAT:
            wrapped = raw.get("research_package")
            if not isinstance(wrapped, Mapping):
                continue
            package = wrapped

        compact = _compact_package(
            package,
            package_path,
            source_format=source_format,
        )
        if compact is None:
            continue
        ticker = str(compact["ticker"])
        if ticker not in wanted:
            continue
        fingerprint = json.dumps(
            {key: value for key, value in compact.items() if key != "source_path"},
            sort_keys=True,
            default=str,
        )
        if fingerprint in seen_fingerprints:
            continue
        seen_fingerprints.add(fingerprint)
        packages_by_ticker[ticker].append(compact)

    return {
        "policy": {
            "authority": "EXACT_DURABLE_PRIOR_SUBJECT_RECORDS",
            "scientific_reinterpretation_by_deterministic_code": False,
            "raw_rows_present": False,
            "purpose": "Give Sol prior findings/hypotheses/closures while raw reproducible data is reacquired separately.",
        },
        "subjects": [
            {"subject_id": f"equity:{ticker}", "ticker": ticker, "research_packages": packages_by_ticker[ticker]}
            for ticker in tickers
        ],
    }


def _prior_memory_documents(root: Path) -> tuple[Mapping[str, object], ...]:
    documents: list[Mapping[str, object]] = []
    seen: set[str] = set()
    for path in sorted(root.glob("mts-v4-*/**/cross_subject_memory.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(raw, Mapping):
            continue
        fingerprint = json.dumps(raw, sort_keys=True, default=str)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        documents.append({"source_path": str(path), "document": raw})
    return tuple(documents)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run an explicit Sol-controlled cross-subject generalization campaign. All selected ticker data is "
            "reacquired into temporary cache; prior durable scientific records are supplied as context."
        )
    )
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument("--ticker", action="append", default=[])
    parser.add_argument("--state-dir")
    parser.add_argument("--sol-spend-limit-usd", type=float, default=DEFAULT_AUTHORIZED_SOL_SPEND_USD)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = Path(args.root).expanduser().resolve()
    discovered = set(_discover_tickers(root))
    discovered.update(item.strip().upper() for item in args.ticker if item.strip())
    tickers = tuple(sorted(discovered))
    if len(tickers) < 2:
        raise RuntimeError("cross-subject generalization requires at least two previously analyzed tickers")

    historical_context = _historical_subject_context(root, tickers)
    memory_documents = _prior_memory_documents(root)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    state_dir = Path(args.state_dir or f"/home/ubuntu/mts-v4-cross-subject-generalization-{stamp}")

    if args.dry_run:
        print("DRY_RUN=True")
        print(f"TICKER_COUNT={len(tickers)}")
        print("TICKERS=" + ",".join(tickers))
        print(f"PRIOR_MEMORY_DOCUMENTS={len(memory_documents)}")
        for index, memory_document in enumerate(memory_documents, start=1):
            print(f"PRIOR_MEMORY_DOCUMENT_{index}_SOURCE={memory_document['source_path']}")
        subjects = historical_context.get("subjects", [])
        package_count = sum(
            len(item.get("research_packages", []))
            for item in subjects
            if isinstance(item, Mapping)
        )
        print(f"HISTORICAL_RESEARCH_PACKAGES={package_count}")
        print(f"STATE_DIR={state_dir}")
        print("RAW_DATA_POLICY=REACQUIRE_TO_TEMPORARY_CACHE_ONLY")
        print("ANALYSIS_AUTHORITY=SOL_ONLY")
        return 0

    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")
    state_dir.mkdir(parents=True, exist_ok=False)
    os.environ.setdefault("MTS_SOL_TELEMETRY_PATH", str(state_dir / "sol_transport_telemetry.jsonl"))

    program_subject = SubjectMetadata(
        subject_id=GENERALIZATION_SUBJECT_ID,
        ticker="MULTI",
        asset_class="RESEARCH_PROGRAM",
        attributes={"member_subject_ids": [f"equity:{ticker}" for ticker in tickers]},
    )
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SolCrossSubjectGeneralizationResearchDirector(
        research_package_store=package_store,
        historical_subject_context=historical_context,
        prior_cross_subject_memory_documents=memory_documents,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=GENERALIZATION_SUBJECT_ID,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=args.sol_spend_limit_usd,
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=GENERALIZATION_MISSION,
        nexus_path=state_dir / "research_nexus.json",
    )

    intake = IntakeEngine(runtime.cache)
    original_evidence = []
    coverage: dict[str, list[str]] = {}
    for ticker in tickers:
        subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
        acquired = intake.ingest(subject=subject, source=standard_live_market_source())
        original_evidence.extend(acquired)
        coverage[ticker] = [item.evidence_id for item in acquired]

    evidence = generalization_evidence_view(original_evidence)
    (state_dir / "generalization_corpus.json").write_text(
        json.dumps(
            {
                "tickers": tickers,
                "evidence_by_ticker": coverage,
                "historical_subject_context": historical_context,
                "prior_cross_subject_memory_documents": memory_documents,
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n",
        encoding="utf-8",
    )

    decision_path = state_dir / "batch_decisions.jsonl"
    report_path = state_dir / "batch_reports.jsonl"
    latest_report: BatchExecutionReport | None = None
    campaign_id = f"mts-v4-cross-subject-generalization-{stamp}"

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=program_subject,
            request=request,
        )

    def on_report(report, decisions, analyses):
        nonlocal latest_report
        latest_report = report
        recorder.record_report(report)
        _append_jsonl(
            report_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decisions": decisions,
                "analyses_executed": analyses,
                "report": asdict(report),
            },
        )

    def on_decision(decision, decisions, analyses):
        recorder.record_plan(
            campaign_id=campaign_id,
            subject=program_subject,
            decision=decision,
        )
        recorder.record_predictive_hypothesis_updates(
            decision,
            current_report=latest_report,
        )
        recorder.record_closures(decision)
        _append_jsonl(
            decision_path,
            {
                "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
                "decision_sequence": decisions,
                "analyses_executed": analyses,
                "decision": asdict(decision),
            },
        )

    try:
        outcome = runtime.orchestrator.run(
            subject=program_subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"STATE_DIR={state_dir}", flush=True)
        print("HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
        print(f"AUTHORIZATION_ARTIFACT={artifact}", flush=True)
        return 2

    spend = rd.sol_spend_snapshot()
    summary = {
        "campaign_id": campaign_id,
        "subject_id": GENERALIZATION_SUBJECT_ID,
        "tickers": tickers,
        "ticker_count": len(tickers),
        "evidence_descriptor_count": len(evidence),
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(spend) if spend is not None else None,
        "raw_data_policy": "TEMPORARY_REACQUIRED_NOT_DURABLE_NEXUS_ROWS",
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"TICKER_COUNT={len(tickers)}", flush=True)
    print("TICKERS=" + ",".join(tickers), flush=True)
    print(f"EVIDENCE_DESCRIPTORS={len(evidence)}", flush=True)
    print(f"DECISIONS={outcome.decisions}", flush=True)
    print(f"BATCHES={outcome.batches_executed}", flush=True)
    print(f"ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"CLOSED={outcome.closed}", flush=True)
    print(f"CLOSE_REASON={outcome.close_reason}", flush=True)
    if spend is not None:
        print(f"SOL_SPEND_USD={spend.actual_spend_usd:.4f}", flush=True)
    print(f"CORPUS={state_dir / 'generalization_corpus.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())