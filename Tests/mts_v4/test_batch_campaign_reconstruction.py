from __future__ import annotations

from dataclasses import asdict
import json

import pytest

from MTS_V4.batch_campaign_reconstruction import (
    BatchCampaignReconstructionError,
    reconstruct_batched_campaign,
)
from MTS_V4.contracts import (
    AnalysisRequest,
    AnalysisResult,
    EvidenceMetadata,
    ResearchPhase,
    SubjectMetadata,
)
from MTS_V4.nexus_json import JsonResearchNexus
from MTS_V4.research_package_store import JsonResearchPackageStore


def _progress(percent: float) -> dict[str, object]:
    return {
        "estimated_percent_complete": percent,
        "estimated_remaining_batches": 1,
        "estimated_remaining_sol_calls": 1,
        "estimate_confidence": "medium",
        "estimate_rationale": "fixture",
    }


def _decision(*, analysis_id: str, question_id: str, update=None) -> dict[str, object]:
    return {
        "continue_research": True,
        "research_packages": [
            {
                "rp_id": "RP-1",
                "parent_rp_id": None,
                "objective": "Recover the existing scientific line without changing it.",
                "decision_boundary": None,
                "analyses": [
                    {
                        "analysis_id": analysis_id,
                        "rp_id": "RP-1",
                        "question_id": question_id,
                        "parent_question_id": None,
                        "parent_rp_id": None,
                        "subject_id": "equity:AMD",
                        "question": f"Question for {analysis_id}",
                        "method_id": "analysis.test",
                        "inputs": [
                            {
                                "role": "daily",
                                "evidence_id": "E1",
                                "analysis_id": None,
                                "dataset_name": None,
                            }
                        ],
                        "parameters": {"input_name": "daily"},
                        "research_phase": "EXPLORATION",
                        "rationale": "fixture",
                    }
                ],
            }
        ],
        "rp_closures": [],
        "promote_findings": [],
        "research_state": {
            "predictive_hypothesis_updates": [] if update is None else [update]
        },
        "close_reason": None,
        "batch_interpretation": "fixture",
        "research_progress": _progress(50.0),
    }


def _report_record(*, analysis_id: str, request_id: str, result_id: str) -> dict[str, object]:
    request = AnalysisRequest(
        request_id=request_id,
        subject_id="equity:AMD",
        question=f"Question for {analysis_id}",
        method_id="analysis.test",
        evidence_ids=("E1",),
        parameters={"input_name": "evidence:E1"},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="fixture",
        rp_id="RP-1",
        question_id=f"Q-{analysis_id}",
    )
    result = AnalysisResult(
        result_id=result_id,
        request_id=request_id,
        subject_id="equity:AMD",
        method_id="analysis.test",
        outputs={"value": 1.0},
        evidence_ids=("E1",),
        execution_metadata={
            "execution_status": "SUCCESS",
            "future_information": {"contains_future_information": False},
        },
    )
    return {
        "analysis_id": analysis_id,
        "rp_id": "RP-1",
        "status": "SUCCESS",
        "compiled_request": asdict(request),
        "result": asdict(result),
        "objective_defect": None,
        "binding_map": {"daily": "evidence:E1"},
        "mechanical_repairs": [],
    }


def _write_jsonl(path, rows) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, default=str) + "\n" for row in rows),
        encoding="utf-8",
    )


def _build_nexus(path) -> None:
    nexus = JsonResearchNexus(path)
    subject = SubjectMetadata(subject_id="equity:AMD", ticker="AMD")
    nexus.upsert_subject(subject)
    nexus.upsert_evidence_metadata(
        EvidenceMetadata(
            evidence_id="E1",
            subject_id=subject.subject_id,
            evidence_type="PRICE",
            artifact_type="TABULAR",
            source_identity="fixture",
            coverage_start="2026-01-01",
            coverage_end="2026-09-11",
            row_count=1,
            schema=("close",),
        )
    )
    for request_id, result_id in (("REQ-1", "R1"), ("REQ-2", "R2")):
        nexus.register_analysis_result_metadata(
            AnalysisResult(
                result_id=result_id,
                request_id=request_id,
                subject_id=subject.subject_id,
                method_id="analysis.test",
                outputs={},
                evidence_ids=("E1",),
                execution_metadata={
                    "execution_status": "SUCCESS",
                    "future_information": {"contains_future_information": False},
                },
            ).durable_metadata()
        )


def test_reconstruction_replays_prior_report_before_predictive_update(tmp_path) -> None:
    decisions_path = tmp_path / "decisions.jsonl"
    reports_path = tmp_path / "reports.jsonl"
    nexus_path = tmp_path / "nexus.json"
    package_dir = tmp_path / "packages"
    _build_nexus(nexus_path)

    update = {
        "rp_id": "RP-1",
        "action": "CREATE_TENTATIVE",
        "hypothesis_id": "H1",
        "statement": "A frozen prospective statement.",
        "success_definition": "At least the predeclared outcome.",
        "minimum_required_trials": 2,
        "source_result_ids": ["R1"],
    }
    decisions = [
        {
            "decision_sequence": 1,
            "decision": _decision(analysis_id="A1", question_id="Q-A1"),
            "analyses_executed": 0,
        },
        {
            "decision_sequence": 2,
            "decision": _decision(analysis_id="A2", question_id="Q-A2", update=update),
            "analyses_executed": 1,
        },
    ]
    reports = [
        {
            "decisions": 1,
            "analyses_executed": 1,
            "report": {"records": [_report_record(analysis_id="A1", request_id="REQ-1", result_id="R1")]},
        },
        {
            "decisions": 2,
            "analyses_executed": 2,
            "report": {"records": [_report_record(analysis_id="A2", request_id="REQ-2", result_id="R2")]},
        },
    ]
    _write_jsonl(decisions_path, decisions)
    _write_jsonl(reports_path, reports)

    recovered = reconstruct_batched_campaign(
        decisions_jsonl=decisions_path,
        reports_jsonl=reports_path,
        nexus_json=nexus_path,
        package_store_dir=package_dir,
        campaign_id="recovered-amd",
        subject_id="equity:AMD",
    )

    assert recovered.analyses_executed == 2
    assert set(recovered.results_by_analysis_id) == {"A1", "A2"}
    package = JsonResearchPackageStore(package_dir).load("RP-1")
    assert package is not None
    assert len(package.questions) == 2
    assert len(package.analyses) == 2
    assert [item.result_id for item in package.analyses] == ["R1", "R2"]
    assert len(package.predictive_hypotheses) == 1
    assert package.predictive_hypotheses[0].hypothesis_id == "H1"
    assert package.predictive_hypotheses[0].source_result_ids == ("R1",)


def test_reconstruction_rejects_decision_report_membership_mismatch(tmp_path) -> None:
    decisions_path = tmp_path / "decisions.jsonl"
    reports_path = tmp_path / "reports.jsonl"
    nexus_path = tmp_path / "nexus.json"
    _build_nexus(nexus_path)
    _write_jsonl(
        decisions_path,
        [{"decision_sequence": 1, "decision": _decision(analysis_id="A1", question_id="Q-A1")}],
    )
    _write_jsonl(
        reports_path,
        [
            {
                "decisions": 1,
                "analyses_executed": 1,
                "report": {
                    "records": [_report_record(analysis_id="WRONG", request_id="REQ-1", result_id="R1")]
                },
            }
        ],
    )

    with pytest.raises(BatchCampaignReconstructionError, match="analysis membership mismatch"):
        reconstruct_batched_campaign(
            decisions_jsonl=decisions_path,
            reports_jsonl=reports_path,
            nexus_json=nexus_path,
            package_store_dir=tmp_path / "packages",
            campaign_id="recovered-amd",
            subject_id="equity:AMD",
        )
