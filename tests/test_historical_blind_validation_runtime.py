from __future__ import annotations

from MTS_V4.blind_validation_runtime import BlindPredictionValidator
from MTS_V4.contracts import AnalysisRequest, EvidenceDescriptor, ResearchPhase
from MTS_V4.method_catalog import MethodCatalog, MethodSpec


def _catalog() -> MethodCatalog:
    catalog = MethodCatalog()
    catalog.register(
        MethodSpec(
            method_id="analysis.fixture",
            description="fixture",
            artifact_types=("NORMALIZED_ROW_DATASET",),
            exploration_allowed=True,
            validation_allowed=True,
            allows_future_information=False,
        )
    )
    return catalog


def _evidence() -> dict[str, EvidenceDescriptor]:
    item = EvidenceDescriptor(
        evidence_id="evidence:equity:AAPL:1",
        subject_id="equity:AAPL",
        evidence_type="OHLCV",
        artifact_type="NORMALIZED_ROW_DATASET",
        source_identity="fixture",
        coverage_start="2026-01-01",
        coverage_end="2026-01-02",
        row_count=2,
        schema=("date", "close"),
        cache_key="blind:1",
    )
    return {item.evidence_id: item}


def _request(phase: ResearchPhase) -> AnalysisRequest:
    return AnalysisRequest(
        request_id="req:1",
        subject_id="equity:AAPL",
        question="Evaluate frozen hypothesis.",
        method_id="analysis.fixture",
        evidence_ids=("evidence:equity:AAPL:1",),
        parameters={},
        research_phase=phase,
    )


def test_blind_prediction_runtime_rejects_exploration_phase():
    validator = BlindPredictionValidator(_catalog())
    defects = validator.validate(_request(ResearchPhase.EXPLORATION), _evidence())
    assert any(
        item.code == "BLIND_VALIDATION_REQUIRES_VALIDATION_PHASE"
        for item in defects
    )


def test_blind_prediction_runtime_accepts_validation_phase():
    validator = BlindPredictionValidator(_catalog())
    defects = validator.validate(_request(ResearchPhase.VALIDATION), _evidence())
    assert not any(
        item.code == "BLIND_VALIDATION_REQUIRES_VALIDATION_PHASE"
        for item in defects
    )
