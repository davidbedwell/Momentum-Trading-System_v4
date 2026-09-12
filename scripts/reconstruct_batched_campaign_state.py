from __future__ import annotations

import argparse
import json
from pathlib import Path

from MTS_V4.batch_campaign_reconstruction import reconstruct_batched_campaign
from MTS_V4.research_package_store import JsonResearchPackageStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct durable batched Research Package state from previously persisted "
            "decision/report artifacts without making Sol calls or re-running Analysis."
        )
    )
    parser.add_argument("--decisions-jsonl", required=True)
    parser.add_argument("--reports-jsonl", required=True)
    parser.add_argument("--nexus-json", required=True)
    parser.add_argument("--output-state-dir", required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--subject-id", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    output_state_dir = Path(args.output_state_dir)
    package_store_dir = output_state_dir / "research_packages"
    reconstructed = reconstruct_batched_campaign(
        decisions_jsonl=args.decisions_jsonl,
        reports_jsonl=args.reports_jsonl,
        nexus_json=args.nexus_json,
        package_store_dir=package_store_dir,
        campaign_id=args.campaign_id,
        subject_id=args.subject_id,
    )
    store = JsonResearchPackageStore(package_store_dir)
    packages = [store.load(rp_id) for rp_id in store.list_ids()]
    summary = {
        "campaign_id": reconstructed.campaign_id,
        "subject_id": reconstructed.subject.subject_id,
        "decisions_replayed": len(reconstructed.decisions),
        "reports_replayed": len(reconstructed.reports),
        "analyses_executed": reconstructed.analyses_executed,
        "results_recovered": len(reconstructed.results_by_analysis_id),
        "findings_promoted": reconstructed.findings_promoted,
        "research_packages": [
            {
                "rp_id": package.rp_id,
                "status": package.status,
                "questions": len(package.questions),
                "analyses": len(package.analyses),
                "completed_results": sum(1 for item in package.analyses if item.result_id is not None),
                "predictive_hypotheses": len(package.predictive_hypotheses),
                "originating_question": package.originating_question,
            }
            for package in packages
            if package is not None
        ],
        "resume_boundary": {
            "ready_for_interpretation": reconstructed.latest_decision.continue_research,
            "prior_decision_research_packages": [
                package.rp_id for package in reconstructed.latest_decision.research_packages
            ],
            "latest_report_records": len(reconstructed.latest_report.records),
        },
        "sol_calls": 0,
        "analysis_executions": 0,
    }
    output_state_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_state_dir / "reconstruction_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"RECONSTRUCTION_SUMMARY={summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
