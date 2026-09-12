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
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.retrospective_recovery import (
    SolRetrospectiveRecoveryResearchDirector,
    load_retrospective_subject_context,
)
from MTS_V4.sol_spend_guard import (
    DEFAULT_AUTHORIZED_SOL_SPEND_USD,
    SolSpendAuthorizationRequired,
)
from scripts.run_sol_cross_subject_generalization import (
    _discover_tickers,
    _historical_subject_context,
)
from scripts.run_sol_retrospective_recovery import (
    _append_jsonl,
    _interactive_spend_authorization,
    _required_env,
)


SEQUENCE = ("AAPL", "MSFT", "XOM")

SEQUENTIAL_RETROSPECTIVE_MISSION = DEFAULT_MISSION + (
    " This is retrospective recovery of a previously exposed subject under the corrected batched Research Director "
    "lifecycle. Historical subject work is discovery context only and is never blind validation. The AI Research "
    "Director also receives compact prior-subject scientific findings and the canonical RD-authored cross-subject "
    "scientific memory/frontier. Use those contexts as nonbinding scientific memory: actively consider transferability, "
    "contradictions, conditional structure, and falsifiable generalization pathways when scientifically useful, but do "
    "not assume that any prior relationship generalizes. Deterministic code does not choose subjects, variables, methods, "
    "thresholds, normalizations, horizons, hypotheses, or generalizations. The AI Research Director retains authority to "
    "test, challenge, reformulate, condition, defer, ignore, or reject prior cross-subject ideas."
)


def _parse_historical_overrides(values: Sequence[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for raw in values:
        ticker, separator, path = raw.partition("=")
        ticker = ticker.strip().upper()
        path = path.strip()
        if not separator or ticker not in SEQUENCE or not path:
            raise ValueError(
                "--historical-subject-dir must use TICKER=/absolute/path for AAPL, MSFT, or XOM"
            )
        if ticker in overrides:
            raise ValueError(f"duplicate historical subject override for {ticker}")
        overrides[ticker] = Path(path).expanduser().resolve()
    return overrides


def _discover_historical_subject_candidates(root: Path, ticker: str) -> tuple[Path, ...]:
    """Discover usable preserved subject directories without ranking competing histories."""
    candidates: set[Path] = set()
    patterns = (
        f"mts-v4-*/subjects/{ticker}",
        f"mts-v4-*/{ticker}",
    )
    for pattern in patterns:
        for path in root.glob(pattern):
            if not path.is_dir():
                continue
            try:
                load_retrospective_subject_context(path)
            except RuntimeError:
                continue
            candidates.add(path.resolve())
    return tuple(sorted(candidates, key=str))


def _resolve_historical_subject_dir(
    root: Path,
    ticker: str,
    overrides: Mapping[str, Path],
) -> Path:
    explicit = overrides.get(ticker)
    if explicit is not None:
        load_retrospective_subject_context(explicit)
        return explicit

    candidates = _discover_historical_subject_candidates(root, ticker)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        raise RuntimeError(
            f"no usable preserved historical subject directory found for {ticker}; "
            f"supply --historical-subject-dir {ticker}=/absolute/path"
        )
    rendered = "\n  ".join(str(path) for path in candidates)
    raise RuntimeError(
        f"multiple preserved historical subject directories found for {ticker}; deterministic code will not choose "
        f"which scientific history is authoritative. Supply an explicit override:\n  {rendered}"
    )


def _compact_prior_subject_science(root: Path, *, active_ticker: str) -> Mapping[str, object]:
    """Expose prior durable scientific conclusions without raw rows or reusable Analysis payloads."""
    tickers = tuple(ticker for ticker in _discover_tickers(root) if ticker != active_ticker)
    historical = _historical_subject_context(root, tickers)
    subjects: list[Mapping[str, object]] = []
    for subject in historical.get("subjects", []):
        if not isinstance(subject, Mapping):
            continue
        packages_out: list[Mapping[str, object]] = []
        for package in subject.get("research_packages", []):
            if not isinstance(package, Mapping):
                continue
            packages_out.append(
                {
                    "source_path": package.get("source_path"),
                    "subject_id": package.get("subject_id"),
                    "ticker": package.get("ticker"),
                    "rp_id": package.get("rp_id"),
                    "campaign_id": package.get("campaign_id"),
                    "parent_rp_id": package.get("parent_rp_id"),
                    "status": package.get("status"),
                    "originating_question": package.get("originating_question"),
                    "originating_rationale": package.get("originating_rationale"),
                    "hypotheses": package.get("hypotheses", []),
                    "predictive_hypotheses": package.get("predictive_hypotheses", []),
                    "findings": package.get("findings", []),
                    "unresolved_issues": package.get("unresolved_issues", []),
                    "close_reason": package.get("close_reason"),
                    "final_assessment": package.get("final_assessment"),
                }
            )
        if packages_out:
            subjects.append(
                {
                    "subject_id": subject.get("subject_id"),
                    "ticker": subject.get("ticker"),
                    "research_packages": packages_out,
                }
            )
    return {
        "policy": {
            "authority": "EXACT_DURABLE_PRIOR_SUBJECT_SCIENCE",
            "raw_rows_present": False,
            "reusable_analysis_payloads_present": False,
            "deterministic_scientific_ranking": False,
            "mandatory_research_agenda": False,
            "rd_may_test_challenge_reformulate_condition_defer_or_ignore": True,
        },
        "subjects": subjects,
    }


def _run_subject(
    *,
    root: Path,
    ticker: str,
    historical_dir: Path,
    state_dir: Path,
    spend_limit_usd: float,
    memory_selection,
    dry_run: bool,
) -> Mapping[str, object]:
    retrospective_context = load_retrospective_subject_context(historical_dir)
    prior_subject_science = _compact_prior_subject_science(root, active_ticker=ticker)
    retrospective_context["prior_subject_scientific_context"] = prior_subject_science
    retrospective_context["cross_subject_memory_provenance"] = {
        "source_path": str(memory_selection.source_path),
        "superseded_paths": [str(path) for path in memory_selection.superseded_paths],
        "frontier_version": (
            memory_selection.store.frontier().version
            if memory_selection.store.frontier() is not None
            else 0
        ),
        "record_count": len(memory_selection.store.records()),
    }

    prior_package_count = sum(
        len(subject.get("research_packages", []))
        for subject in prior_subject_science.get("subjects", [])
        if isinstance(subject, Mapping)
    )

    if dry_run:
        return {
            "ticker": ticker,
            "historical_subject_dir": str(historical_dir),
            "state_dir": str(state_dir),
            "canonical_memory_source": str(memory_selection.source_path),
            "canonical_memory_records": len(memory_selection.store.records()),
            "canonical_memory_frontier_version": (
                memory_selection.store.frontier().version
                if memory_selection.store.frontier() is not None
                else 0
            ),
            "prior_subject_scientific_packages": prior_package_count,
            "closed": None,
            "dry_run": True,
        }

    state_dir.mkdir(parents=True, exist_ok=False)
    telemetry_path = state_dir / "sol_transport_telemetry.jsonl"
    os.environ["MTS_SOL_TELEMETRY_PATH"] = str(telemetry_path)

    subject = SubjectMetadata(subject_id=f"equity:{ticker}", ticker=ticker)
    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    recorder = BatchCampaignResearchRecorder(package_store=package_store)
    rd = SolRetrospectiveRecoveryResearchDirector(
        research_package_store=package_store,
        retrospective_context=retrospective_context,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", "600")),
        required_subject_id=subject.subject_id,
        required_research_phase=ResearchPhase.EXPLORATION,
        sol_spend_limit_usd=spend_limit_usd,
        human_spend_authorization_callback=_interactive_spend_authorization,
    )
    runtime = build_batch_runtime(
        rd=rd,
        mission=SEQUENTIAL_RETROSPECTIVE_MISSION,
        nexus_path=state_dir / "research_nexus.json",
        scientific_memory=memory_selection.store,
    )
    evidence = IntakeEngine(runtime.cache).ingest(
        subject=subject,
        source=standard_live_market_source(),
    )
    campaign_id = state_dir.name

    (state_dir / "retrospective_context.json").write_text(
        json.dumps(retrospective_context, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )

    decision_path = state_dir / "batch_decisions.jsonl"
    report_path = state_dir / "batch_reports.jsonl"
    latest_report: BatchExecutionReport | None = None

    def accepted(request):
        recorder.record_accepted_request(
            campaign_id=campaign_id,
            subject=subject,
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
            subject=subject,
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
            subject=subject,
            evidence=evidence,
            decision_callback=on_decision,
            report_callback=on_report,
            accepted_request_callback=accepted,
        )
    except SolSpendAuthorizationRequired as exc:
        artifact = state_dir / "sol_spend_authorization_required.json"
        artifact.write_text(
            json.dumps(asdict(exc.snapshot), sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "ticker": ticker,
            "state_dir": str(state_dir),
            "closed": False,
            "authorization_required": True,
            "authorization_artifact": str(artifact),
        }

    spend = rd.sol_spend_snapshot()
    summary = {
        "campaign_id": campaign_id,
        "subject_id": subject.subject_id,
        "historical_subject_dir": str(historical_dir),
        "historical_exposure_status": "EXPOSED",
        "research_phase": "EXPLORATION",
        "blind_validation_claim_allowed": False,
        "canonical_cross_subject_memory_source": str(memory_selection.source_path),
        "canonical_cross_subject_memory_record_count": len(memory_selection.store.records()),
        "canonical_cross_subject_frontier_version": (
            memory_selection.store.frontier().version
            if memory_selection.store.frontier() is not None
            else 0
        ),
        "prior_subject_scientific_packages_exposed": prior_package_count,
        "decisions": outcome.decisions,
        "batches_executed": outcome.batches_executed,
        "analyses_executed": outcome.analyses_executed,
        "findings_promoted": outcome.findings_promoted,
        "closed": outcome.closed,
        "close_reason": outcome.close_reason,
        "sol_spend": asdict(spend) if spend is not None else None,
        "sol_transport_telemetry": str(telemetry_path),
    }
    (state_dir / "run_summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run AAPL, then MSFT, then XOM retrospective recovery sequentially. The next subject starts only after "
            "the prior subject closes. Canonical cross-subject memory/frontier and prior durable subject science are "
            "exposed to Sol as nonbinding discovery context."
        )
    )
    parser.add_argument("--root", default="/home/ubuntu")
    parser.add_argument(
        "--historical-subject-dir",
        action="append",
        default=[],
        help="optional explicit TICKER=/absolute/path; repeat for AAPL, MSFT, XOM",
    )
    parser.add_argument(
        "--sol-spend-limit-usd",
        type=float,
        default=DEFAULT_AUTHORIZED_SOL_SPEND_USD,
        help="initial Sol spend authorization per subject",
    )
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.sol_spend_limit_usd <= 0:
        raise RuntimeError("--sol-spend-limit-usd must be positive")

    root = Path(args.root).expanduser().resolve()
    overrides = _parse_historical_overrides(args.historical_subject_dir)
    historical_dirs = {
        ticker: _resolve_historical_subject_dir(root, ticker, overrides)
        for ticker in SEQUENCE
    }

    memory_selection = JsonCrossSubjectScientificMemoryStore.discover_current(root)
    if memory_selection is None:
        raise RuntimeError("no canonical cross-subject scientific memory snapshot is available")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results: list[Mapping[str, object]] = []

    print("SEQUENCE=" + ",".join(SEQUENCE), flush=True)
    print(f"CANONICAL_MEMORY_SOURCE={memory_selection.source_path}", flush=True)
    print(f"CANONICAL_MEMORY_RECORDS={len(memory_selection.store.records())}", flush=True)
    frontier = memory_selection.store.frontier()
    print(f"CANONICAL_MEMORY_FRONTIER_VERSION={frontier.version if frontier is not None else 0}", flush=True)
    for ticker in SEQUENCE:
        print(f"HISTORICAL_{ticker}_DIR={historical_dirs[ticker]}", flush=True)

    for ordinal, ticker in enumerate(SEQUENCE, start=1):
        state_dir = root / f"mts-v4-sequential-rerun-{ordinal:02d}-{ticker.lower()}-{stamp}"
        result = _run_subject(
            root=root,
            ticker=ticker,
            historical_dir=historical_dirs[ticker],
            state_dir=state_dir,
            spend_limit_usd=args.sol_spend_limit_usd,
            memory_selection=memory_selection,
            dry_run=args.dry_run,
        )
        results.append(result)
        print(f"{ticker}_STATE_DIR={state_dir}", flush=True)
        print(f"{ticker}_PRIOR_SUBJECT_SCIENTIFIC_PACKAGES={result.get('prior_subject_scientific_packages') or result.get('prior_subject_scientific_packages_exposed', 0)}", flush=True)
        if args.dry_run:
            continue
        print(f"{ticker}_CLOSED={result.get('closed')}", flush=True)
        if result.get("authorization_required"):
            print(f"{ticker}_HUMAN_SOL_SPEND_AUTHORIZATION_REQUIRED=True", flush=True)
            print(f"{ticker}_AUTHORIZATION_ARTIFACT={result.get('authorization_artifact')}", flush=True)
            print("SEQUENCE_HALTED=True", flush=True)
            return 2
        if result.get("closed") is not True:
            print(
                f"SEQUENCE_HALTED=True: {ticker} did not close, so the next subject will not start.",
                flush=True,
            )
            return 3

    manifest = root / f"MTS_V4_AAPL_MSFT_XOM_SEQUENTIAL_RERUN_{stamp}.json"
    manifest.write_text(
        json.dumps(
            {
                "sequence": SEQUENCE,
                "dry_run": args.dry_run,
                "canonical_memory_source": str(memory_selection.source_path),
                "canonical_memory_superseded_paths": [
                    str(path) for path in memory_selection.superseded_paths
                ],
                "results": results,
            },
            indent=2,
            sort_keys=True,
            default=str,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"SEQUENCE_COMPLETE={not args.dry_run}", flush=True)
    print(f"MANIFEST={manifest}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
