from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.contracts import ResearchPhase
from MTS_V4.research_package import ResearchPackage
from MTS_V4.research_package_store import JsonResearchPackageStore


def _resume_module():
    path = Path("scripts/resume_fresh_subject.py")
    spec = importlib.util.spec_from_file_location("mts_v4_resume_fresh_subject_test", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_resume_recovers_original_campaign_identity_from_durable_packages(tmp_path):
    module = _resume_module()
    store = JsonResearchPackageStore(tmp_path)
    store.create(
        ResearchPackage(
            rp_id="RP-ONE",
            subject_id="equity:NVDA",
            campaign_id="mts-v4-sol-batched-nvda-original",
            originating_question="q",
            originating_rationale="r",
        )
    )
    store.create(
        ResearchPackage(
            rp_id="RP-TWO",
            subject_id="equity:NVDA",
            campaign_id="mts-v4-sol-batched-nvda-original",
            originating_question="q2",
            originating_rationale="r2",
        )
    )

    assert module._recover_campaign_id(
        tmp_path,
        subject_id="equity:NVDA",
    ) == "mts-v4-sol-batched-nvda-original"


def test_resume_rejects_mixed_durable_campaign_identity(tmp_path):
    module = _resume_module()
    store = JsonResearchPackageStore(tmp_path)
    for index, campaign_id in enumerate(("campaign-a", "campaign-b"), start=1):
        store.create(
            ResearchPackage(
                rp_id=f"RP-{index}",
                subject_id="equity:NVDA",
                campaign_id=campaign_id,
                originating_question="q",
                originating_rationale="r",
            )
        )

    with pytest.raises(RuntimeError, match="multiple campaign identities"):
        module._recover_campaign_id(
            tmp_path,
            subject_id="equity:NVDA",
        )


def test_resume_counts_all_durable_checkpoint_records(tmp_path):
    module = _resume_module()
    checkpoints = tmp_path / "continuation_analysis_checkpoints.jsonl"
    checkpoints.write_text(
        "\n".join(
            (
                json.dumps({"decision_sequence": 6, "record": {"analysis_id": "a:1"}}),
                "",
                json.dumps({"decision_sequence": 6, "record": {"analysis_id": "a:2"}}),
                json.dumps({"decision_sequence": 7, "record": {"analysis_id": "a:3"}}),
            )
        )
        + "\n",
        encoding="utf-8",
    )

    assert module._jsonl_record_count(checkpoints) == 3
    assert module._jsonl_record_count(tmp_path / "missing.jsonl") == 0


def test_resume_spend_sums_calls_across_separate_resume_invocations(tmp_path):
    module = _resume_module()
    telemetry = tmp_path / "resume_sol_transport_telemetry.jsonl"
    rows = [
        {
            "event": "SOL_CALL_COMPLETE",
            "estimated_call_cost_usd": 0.423176,
            "estimated_cumulative_sol_spend_usd": 0.423176,
        },
        {
            "event": "SOL_CALL_COMPLETE",
            "estimated_call_cost_usd": 0.400000,
            "estimated_cumulative_sol_spend_usd": 0.400000,
        },
    ]
    telemetry.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )

    assert module._telemetry_spend(telemetry) == pytest.approx(0.823176)


def test_resume_replaces_only_authorized_direct_evidence_references():
    module = _resume_module()
    decision = BatchResearchDecision(
        continue_research=True,
        research_packages=(
            ResearchPackagePlan(
                rp_id="RP-XOM",
                objective="fixture",
                analyses=(
                    ScientificAnalysisSpecification(
                        analysis_id="analysis:xom",
                        rp_id="RP-XOM",
                        question_id="question:xom",
                        subject_id="equity:XOM",
                        question="fixture",
                        method_id="analysis.dataset.compose",
                        inputs=(
                            ScientificInputReference(
                                role="events",
                                evidence_id="evidence:old",
                            ),
                            ScientificInputReference(
                                role="prior",
                                analysis_id="analysis:prior",
                            ),
                        ),
                        parameters={},
                        research_phase=ResearchPhase.EXPLORATION,
                    ),
                ),
            ),
        ),
    )

    refreshed = module._replace_direct_evidence_ids(
        decision,
        {"evidence:old": "evidence:new"},
    )

    inputs = refreshed.research_packages[0].analyses[0].inputs
    assert inputs[0].evidence_id == "evidence:new"
    assert inputs[0].analysis_id is None
    assert inputs[1] == decision.research_packages[0].analyses[0].inputs[1]
    assert decision.research_packages[0].analyses[0].inputs[0].evidence_id == "evidence:old"


def test_resume_evidence_refresh_is_explicit_and_audited():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    assert "--authorize-evidence-refresh" in text
    assert "EXPLICIT_HUMAN_SAME_SOURCE_REFRESH" in text
    assert "resume_interpretation_decision.pre_evidence_refresh.json" in text
    assert "authorized_evidence_refresh.json" in text
    assert "evidence refresh is forbidden after continuation Analysis" in text


def test_resume_persists_paid_sol_decision_before_package_recording():
    text = Path("scripts/resume_fresh_subject.py").read_text(encoding="utf-8")

    interpret = text.index("decision = rd.interpret_batch_results(")
    pending_write = text.index("pending_resume_decision_path.write_text(", interpret)
    record_plan = text.index("recorder.record_plan(", pending_write)

    assert interpret < pending_write < record_plan
    assert "campaign_id = state_dir.name" not in text
