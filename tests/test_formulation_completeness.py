from __future__ import annotations

from MTS_V4.formulation_completeness import (
    FormulationCompletenessContract,
    has_natural_zero_boundary,
)
from MTS_V4.batch_contracts import BatchResearchDecision
from MTS_V4.research_package import ResearchAnalysisRecord, ResearchPackage, ResearchQuestionRecord
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.sol_spend_guard import SolResearchProgressEstimate


def _analysis(*, predictor: str, outcome: str, status: str = "SUCCESS"):
    return ResearchAnalysisRecord(
        request_id=f"request:{predictor}:{outcome}",
        question_id=f"question:{predictor}:{outcome}",
        method_id="analysis.cross_sectional.cohort_effect",
        parameters={
            "cohort_column": predictor,
            "outcome_column": outcome,
            "date_column": "effective_date",
            "threshold": 0,
            "direction": "GE",
        },
        evidence_ids=(),
        analysis_inputs=(),
        execution_status=status,
    )


def test_natural_zero_boundary_uses_feature_semantics_not_hidden_control_identity():
    assert has_natural_zero_boundary("close_to_sma_20__v1")
    assert has_natural_zero_boundary("sma20_slope_5__v1")
    assert has_natural_zero_boundary("return_126__v1")
    assert has_natural_zero_boundary("earnings_surprise_pct__v1")
    assert not has_natural_zero_boundary("return_126_percentile__v1")
    assert not has_natural_zero_boundary("natr_20__v1")
    assert not has_natural_zero_boundary("deterministic_null__v1")


def test_contract_requires_every_signed_predictor_outcome_pair_before_closure():
    contract = FormulationCompletenessContract.from_columns(
        subject_id="universe:test",
        predictor_columns=("close_to_sma_20__v1", "sma20_slope_5__v1", "natr_20__v1"),
        outcome_columns=("forward_return_20__v1", "forward_return_63__v1"),
    )
    assert contract is not None
    analyses = [
        _analysis(predictor=predictor, outcome=outcome)
        for predictor in contract.signed_predictor_columns
        for outcome in contract.outcome_columns
        if (predictor, outcome) != ("sma20_slope_5__v1", "forward_return_63__v1")
    ]

    defect = contract.closure_defect(analyses)

    assert defect is not None
    assert "sma20_slope_5__v1->forward_return_63__v1" in defect
    assert "natr_20__v1" not in defect


def test_contract_round_trips_as_frozen_resume_state():
    contract = FormulationCompletenessContract.from_columns(
        subject_id="universe:test",
        predictor_columns=("return_63__v1", "natr_20__v1"),
        outcome_columns=("forward_return_20__v1",),
    )
    assert contract is not None

    assert FormulationCompletenessContract.from_mapping(contract.to_mapping()) == contract


def test_contract_accepts_only_successful_zero_boundary_positive_cohorts():
    contract = FormulationCompletenessContract.from_columns(
        subject_id="universe:test",
        predictor_columns=("return_63__v1",),
        outcome_columns=("forward_return_20__v1",),
    )
    assert contract is not None
    failed = _analysis(
        predictor="return_63__v1",
        outcome="forward_return_20__v1",
        status="OBJECTIVE_CONTRACT_DEFECT",
    )
    assert contract.closure_defect((failed,)) is not None

    completed = _analysis(
        predictor="return_63__v1",
        outcome="forward_return_20__v1",
    )
    assert contract.closure_defect((completed,)) is None


def _closed_decision():
    return BatchResearchDecision(
        continue_research=False,
        close_reason="The subject is scientifically complete.",
        research_progress=SolResearchProgressEstimate(
            estimated_percent_complete=100,
            estimated_remaining_batches=0,
            estimated_remaining_sol_calls=0,
            estimate_confidence="high",
            estimate_rationale="All justified work is complete.",
        ),
    )


def _provider_with_package(tmp_path, analyses):
    store = JsonResearchPackageStore(tmp_path / "research_packages")
    package = ResearchPackage(
        rp_id="RP-TREND",
        subject_id="universe:test",
        campaign_id="campaign:test",
        originating_question="Does trend contain predictive information?",
        originating_rationale="Test the supplied signed predictors.",
        questions=(
            ResearchQuestionRecord(
                question_id="Q-TREND",
                question="Compare signed trend states.",
                rationale="Zero separates the feature's defined states.",
                research_phase="EXPLORATION",
            ),
        ),
        analyses=tuple(analyses),
    )
    store.create(package)
    contract = FormulationCompletenessContract.from_columns(
        subject_id="universe:test",
        predictor_columns=("close_to_sma_20__v1",),
        outcome_columns=("forward_return_63__v1",),
    )
    assert contract is not None
    return SolBatchResearchDirector(
        research_package_store=store,
        base_url="http://example.invalid",
        model="test-model",
        formulation_completeness_contract=contract,
    )


def test_provider_mechanically_rejects_subject_closure_with_missing_signed_cohort(tmp_path):
    provider = _provider_with_package(tmp_path, ())

    defect = provider._batch_decision_defect(_closed_decision())

    assert defect is not None
    assert "subject closure is blocked" in defect
    assert "close_to_sma_20__v1->forward_return_63__v1" in defect


def test_provider_accepts_subject_closure_after_successful_signed_cohort(tmp_path):
    provider = _provider_with_package(
        tmp_path,
        (
            _analysis(
                predictor="close_to_sma_20__v1",
                outcome="forward_return_63__v1",
            ),
        ),
    )

    assert provider._batch_decision_defect(_closed_decision()) is None
