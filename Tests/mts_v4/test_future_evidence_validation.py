from __future__ import annotations

from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, ResearchPhase
from MTS_V4.standard_methods import standard_method_catalog
from MTS_V4.validation import ObjectiveContractValidator


def _outcome_evidence() -> EvidenceDescriptor:
    return EvidenceDescriptor(
        evidence_id="outcomes",
        subject_id="universe:sp500",
        evidence_type="DERIVED_MARKET_PANEL",
        artifact_type="NORMALIZED_DATASET",
        source_identity="fixture",
        coverage_start="2026-01-01",
        coverage_end="2026-01-31",
        row_count=10,
        schema=("security_id", "effective_date", "forward_return_20__v1"),
        cache_key="cache:outcomes",
        provenance={"contains_future_outcomes": True},
    )


def test_validation_rejects_direct_future_outcome_evidence_even_for_neutral_method():
    request = AnalysisRequest(
        request_id="request:validation",
        subject_id="universe:sp500",
        question="Inspect without look-ahead.",
        method_id="analysis.descriptive.statistics",
        evidence_ids=("outcomes",),
        parameters={"columns": ["forward_return_20__v1"]},
        research_phase=ResearchPhase.VALIDATION,
    )
    defects = ObjectiveContractValidator(standard_method_catalog()).validate(
        request, {"outcomes": _outcome_evidence()}
    )
    assert any(defect.code == "TEMPORAL_CONTRACT_VIOLATION" for defect in defects)


def test_exploration_allows_explicit_historical_outcome_evidence():
    request = AnalysisRequest(
        request_id="request:exploration",
        subject_id="universe:sp500",
        question="Explore historical outcomes.",
        method_id="analysis.descriptive.statistics",
        evidence_ids=("outcomes",),
        parameters={"columns": ["forward_return_20__v1"]},
        research_phase=ResearchPhase.EXPLORATION,
    )
    defects = ObjectiveContractValidator(standard_method_catalog()).validate(
        request, {"outcomes": _outcome_evidence()}
    )
    assert defects == ()
