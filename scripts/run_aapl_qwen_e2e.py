from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from MTS_V4.appeal_provider import AppellateResearchDirector
from MTS_V4.bootstrap import build_runtime
from MTS_V4.campaign import CheckpointedCampaignRunner
from MTS_V4.checkpoint import JsonCampaignCheckpointStore
from MTS_V4.contracts import ResearchDecision, SubjectMetadata
from MTS_V4.decision_journal import JsonResearchDecisionJournal
from MTS_V4.intake import IntakeEngine
from MTS_V4.live_sources import standard_live_market_source
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.research_recording import CampaignResearchRecorder
from MTS_V4.rp_appeal_provider import RPRepresentationAppellateResearchDirector
from MTS_V4.sol_provider import SolResearchPackageAwareResearchDirector


class DiagnosticResearchPackageAwareResearchDirector(RPRepresentationAppellateResearchDirector):
    """Live-run diagnostic wrapper that exposes objective RP representation defects."""

    def _decision_representation_defect(
        self,
        operation: str,
        decision: ResearchDecision,
        payload: Mapping[str, object],
    ) -> str | None:
        defect = super()._decision_representation_defect(operation, decision, payload)
        if defect is not None:
            print(
                "RP_REPRESENTATION_DEFECT="
                + json.dumps(
                    {
                        "operation": operation,
                        "defect": defect,
                        "decision_rp_id": decision.rp_id,
                        "next_request_id": (
                            decision.next_request.request_id
                            if decision.next_request is not None
                            else None
                        ),
                        "next_question_id": (
                            decision.next_request.question_id
                            if decision.next_request is not None
                            else None
                        ),
                        "next_rp_id": (
                            decision.next_request.rp_id
                            if decision.next_request is not None
                            else None
                        ),
                    },
                    sort_keys=True,
                    default=str,
                ),
                flush=True,
            )
        return defect


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"required environment variable is not set: {name}")
    return value


def main() -> None:
    max_analyses = int(os.getenv("MTS_E2E_MAX_ANALYSES", "500"))
    timeout_seconds = int(os.getenv("MTS_RD_TIMEOUT_SECONDS", "600"))
    sol_timeout_seconds = int(os.getenv("MTS_SOL_TIMEOUT_SECONDS", str(timeout_seconds)))
    resume_state_dir = os.getenv("MTS_E2E_RESUME_STATE_DIR")

    if resume_state_dir:
        state_dir = Path(resume_state_dir)
        checkpoint_store = JsonCampaignCheckpointStore(state_dir / "checkpoint.json")
        checkpoint = checkpoint_store.load()
        if checkpoint is None:
            raise RuntimeError(f"no active checkpoint found in resume state directory: {state_dir}")
        campaign_id = checkpoint.campaign_id
        subject = checkpoint.subject
        resume = True
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        state_dir = Path(f"/home/ubuntu/mts-v4-aapl-qwen-e2e-{stamp}")
        state_dir.mkdir(parents=True, exist_ok=False)
        checkpoint_store = JsonCampaignCheckpointStore(state_dir / "checkpoint.json")
        campaign_id = f"mts-v4-aapl-qwen-e2e-{stamp}"
        subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
        resume = False

    package_store = JsonResearchPackageStore(state_dir / "research_packages")
    sol_rd = SolResearchPackageAwareResearchDirector(
        research_package_store=package_store,
        base_url=_required_env("MTS_SOL_BASE_URL"),
        model=_required_env("MTS_SOL_MODEL"),
        api_key=_required_env("MTS_SOL_API_KEY"),
        timeout_seconds=sol_timeout_seconds,
    )
    primary_rd = DiagnosticResearchPackageAwareResearchDirector(
        appeal=sol_rd,
        research_package_store=package_store,
        timeout_seconds=timeout_seconds,
    )
    rd = AppellateResearchDirector(
        primary=primary_rd,
        appeal=sol_rd,
        primary_repair_attempts=3,
    )
    runtime = build_runtime(
        rd=rd,
        nexus_path=state_dir / "research_nexus.json",
        # Three local repair attempts plus one authorized Sol appeal attempt.
        max_contract_repairs=4,
    )

    intake = IntakeEngine(runtime.cache)
    evidence = intake.ingest(
        subject=subject,
        source=standard_live_market_source(),
    )

    recorder = CampaignResearchRecorder(
        package_store=package_store,
        decision_journal=JsonResearchDecisionJournal(state_dir / "rd_decisions.jsonl"),
    )
    runner = CheckpointedCampaignRunner(
        orchestrator=runtime.orchestrator,
        cache=runtime.cache,
        checkpoint_store=checkpoint_store,
        research_recorder=recorder,
    )

    print(f"STATE_DIR={state_dir}", flush=True)
    print(f"CAMPAIGN_ID={campaign_id}", flush=True)
    print(f"RESUME={resume}", flush=True)
    print(f"MAX_ANALYSES={max_analyses}", flush=True)
    print("RD_PRIMARY_PROVIDER=LOCAL_QWEN", flush=True)
    print(f"RD_APPEAL_PROVIDER={_required_env('MTS_SOL_MODEL')}", flush=True)
    print("RD_APPEAL_AFTER_PRIMARY_REPAIRS=3", flush=True)
    print("RD_RP_REPRESENTATION_APPEAL_AFTER_PRIMARY_REPAIRS=3", flush=True)
    print(f"EVIDENCE_COUNT={len(evidence)}", flush=True)
    for item in evidence:
        print(
            "EVIDENCE="
            + json.dumps(
                {
                    "evidence_id": item.evidence_id,
                    "evidence_type": item.evidence_type,
                    "source_identity": item.source_identity,
                    "coverage_start": item.coverage_start,
                    "coverage_end": item.coverage_end,
                    "row_count": item.row_count,
                    "schema": list(item.schema),
                },
                sort_keys=True,
                default=str,
            ),
            flush=True,
        )

    if resume:
        outcome = runner.resume(
            reacquired_evidence=evidence,
            max_analyses=max_analyses,
        )
    else:
        outcome = runner.run_new(
            campaign_id=campaign_id,
            subject=subject,
            evidence=evidence,
            max_analyses=max_analyses,
        )

    print(f"OUTCOME_DECISIONS={outcome.decisions}", flush=True)
    print(f"OUTCOME_ANALYSES={outcome.analyses_executed}", flush=True)
    print(f"OUTCOME_FINDINGS_PROMOTED={outcome.findings_promoted}", flush=True)
    print(f"OUTCOME_CLOSED={outcome.closed}", flush=True)
    print(f"OUTCOME_CLOSE_REASON={outcome.close_reason}", flush=True)
    print(
        "FINAL_DECISION="
        + json.dumps(
            {
                "continue_research": outcome.final_decision.continue_research,
                "rp_id": outcome.final_decision.rp_id,
                "close_reason": outcome.final_decision.close_reason,
                "research_state": outcome.final_decision.research_state,
            },
            sort_keys=True,
            default=str,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
