from __future__ import annotations

from MTS_V4.contracts import AnalysisRequest, AnalysisResultInput, ResearchPhase
from MTS_V4.method_catalog import MethodCatalog, MethodSpec
from MTS_V4.validation import ObjectiveContractValidator


def _request(*, evidence_ids=(), analysis_inputs=()):
    return AnalysisRequest(
        request_id="req:test",
        subject_id="equity:AAPL",
        question="Test runtime recovery guidance",
        method_id="analysis.test",
        evidence_ids=tuple(evidence_ids),
        analysis_inputs=tuple(analysis_inputs),
        parameters={},
        research_phase=ResearchPhase.EXPLORATION,
        rationale="Exercise objective stale-reference guidance.",
        rp_id="RP-0001",
        question_id="Q-0001",
    )


def _validator():
    return ObjectiveContractValidator(
        MethodCatalog(
            [
                MethodSpec(
                    method_id="analysis.test",
                    artifact_types=(),
                )
            ]
        )
    )


def test_missing_evidence_defect_explicitly_forbids_stale_id_reuse():
    stale_id = "evidence:equity:AAPL:stale"
    defects = _validator().validate(
        _request(evidence_ids=(stale_id,)),
        evidence={},
        analysis_results={},
    )

    assert len(defects) == 1
    defect = defects[0]
    assert defect.code == "MISSING_EVIDENCE"
    assert stale_id in defect.message
    assert "Do not reuse this unavailable evidence_id" in defect.message
    assert "currently advertised evidence_id" in defect.message
    assert "Deterministic code will not select a replacement" in defect.message


def test_missing_analysis_result_defect_explicitly_forbids_stale_result_reuse():
    stale_result_id = "analysis-result:stale"
    reference = AnalysisResultInput(
        result_id=stale_result_id,
        output_path=("derived_datasets", "composed_dataset"),
        input_name="aligned_data",
    )
    defects = _validator().validate(
        _request(analysis_inputs=(reference,)),
        evidence={},
        analysis_results={},
    )

    assert len(defects) == 1
    defect = defects[0]
    assert defect.code == "MISSING_ANALYSIS_RESULT"
    assert stale_result_id in defect.message
    assert "Do not reference this unavailable result_id again" in defect.message
    assert "reconstruct or regenerate the needed intermediate result" in defect.message
    assert "currently available evidence" in defect.message
    assert "requires its own new request_id" in defect.message
    assert "Deterministic code will not select" in defect.message


def test_analysis_result_misplaced_as_evidence_gets_current_runtime_guidance():
    stale_result_id = "analysis-result:stale"
    defects = _validator().validate(
        _request(evidence_ids=(stale_result_id,)),
        evidence={},
        analysis_results={},
    )

    assert len(defects) == 1
    defect = defects[0]
    assert defect.code == "MISSING_EVIDENCE"
    assert "Do not reuse this unavailable identifier" in defect.message
    assert "analysis-result IDs are not evidence_ids" in defect.message
    assert "currently available in the active campaign runtime" in defect.message
