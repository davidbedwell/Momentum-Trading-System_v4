from __future__ import annotations

from MTS_V4.qwen_shadow_gate import QwenShadowObservation, evaluate_qwen_shadow_gate


def _observation(case_id: str, analyses: int, reviewed: bool = False):
    kwargs = {}
    if reviewed:
        kwargs = {
            "continued_scientific_loop": True,
            "used_available_toolkit": True,
            "reached_cross_evidence_relationships": True,
            "handled_lack_resource_without_stalling": True,
            "produced_market_science_not_infrastructure_notes": True,
            "scientific_usefulness_assessment": "reviewed against Sol benchmark",
            "unnecessary_analysis_assessment": "reviewed for avoidable work",
        }
    return QwenShadowObservation(case_id, True, True, True, analyses, **kwargs)


def test_gate_preserves_approved_twenty_analysis_floor_and_never_authorizes():
    report = evaluate_qwen_shadow_gate((_observation("a", 19),))
    assert report.autonomy_status == "INSUFFICIENT_SHADOW_EXPOSURE"
    assert report.human_authorization_required is True
    report = evaluate_qwen_shadow_gate((_observation("a", 20),))
    assert report.autonomy_status == "AWAITING_SCIENTIFIC_AUTONOMY_REVIEW"
    report = evaluate_qwen_shadow_gate((_observation("a", 20, reviewed=True),))
    assert report.autonomy_status == "READY_FOR_HUMAN_AUTONOMY_DECISION"
    assert report.human_authorization_required is True
