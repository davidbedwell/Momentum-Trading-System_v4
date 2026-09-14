from __future__ import annotations

from pathlib import Path

import pytest

from MTS_V4.batch_contracts import (
    BatchResearchDecision,
    ResearchPackagePlan,
    ScientificAnalysisSpecification,
    ScientificInputReference,
)
from MTS_V4.batch_research_recording import (
    BatchCampaignResearchRecorder,
    BatchResearchRecordingError,
)
from MTS_V4.contracts import ResearchPhase, SubjectMetadata
from MTS_V4.research_package_store import JsonResearchPackageStore


def _analysis(*, analysis_id: str, rp_id: str, question_id: str, parent_question_id=None):
    return ScientificAnalysisSpecification(
        analysis_id=analysis_id,
        rp_id=rp_id,
        question_id=question_id,
        subject_id="equity:XOM",
        question=question_id,
        method_id="analysis.descriptive.statistics",
        inputs=(ScientificInputReference(role="rows", evidence_id="evidence:xom"),),
        parameters={"columns": ["close"]},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="fixture",
        parent_question_id=parent_question_id,
    )


def test_invalid_cross_package_question_lineage_is_atomic(tmp_path):
    store = JsonResearchPackageStore(tmp_path)
    recorder = BatchCampaignResearchRecorder(package_store=store)
    decision = BatchResearchDecision(
        continue_research=True,
        research_packages=(
            ResearchPackagePlan(
                rp_id="RP-XOM-CATALYST",
                objective="inventory",
                analyses=(
                    _analysis(
                        analysis_id="analysis:inventory",
                        rp_id="RP-XOM-CATALYST",
                        question_id="question:xom:catalyst-inventory",
                    ),
                ),
            ),
            ResearchPackagePlan(
                rp_id="RP-XOM-EARNINGS",
                objective="earnings drift",
                parent_rp_id="RP-XOM-CATALYST",
                analyses=(
                    _analysis(
                        analysis_id="analysis:earnings",
                        rp_id="RP-XOM-EARNINGS",
                        question_id="question:xom:earnings-drift",
                        parent_question_id="question:xom:catalyst-inventory",
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(BatchResearchRecordingError, match="question lineage cannot be resolved"):
        recorder.record_plan(
            campaign_id="campaign:xom",
            subject=SubjectMetadata(subject_id="equity:XOM", ticker="XOM"),
            decision=decision,
        )

    assert store.list_ids() == ()


def test_fresh_runner_persists_decision_before_recording():
    text = Path("scripts/run_sol_batched_one_subject.py").read_text(encoding="utf-8")
    callback = text.index("def on_decision(")
    pending_write = text.index("_write_json_atomic(", callback)
    record_plan = text.index("recorder.record_plan(", pending_write)
    decision_log = text.index("_append_jsonl(", record_plan)
    pending_unlink = text.index("pending_decision_path.unlink()", decision_log)

    assert pending_write < record_plan < decision_log < pending_unlink


def test_sol_contract_explains_package_scoped_question_lineage():
    text = Path("MTS_V4/sol_batch_provider.py").read_text(encoding="utf-8")
    assert "A parent_question_id may name only a question in the same RP" in text
    assert "Never point a question directly into another RP" in text
