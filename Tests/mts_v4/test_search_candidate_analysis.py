from MTS_V4.computational_search import Candidate
from MTS_V4.search_candidate_analysis import SearchCandidateAnalysisEvaluator


def _rows():
    predictors=[]
    outcomes=[]
    for i in range(80):
        date=f"2025-01-{(i%28)+1:02d}-{i:03d}"
        predictors.append({
            "security_id":"S1","effective_date":date,
            "return_20__v1":i/100.0,
            "breadth_above_sma_200__v1":0.7,
            "breadth_positive_20__v1":0.6,
        })
        outcomes.append({
            "security_id":"S1","effective_date":date,
            "forward_return_5__v1":0.02 if i>=40 else -0.01,
        })
    return predictors,outcomes


def test_search_candidate_evaluation_runs_through_analysis_boundary():
    predictors,outcomes=_rows()
    evaluator=SearchCandidateAnalysisEvaluator.build(
        subject_id="equity:TEST", predictor_rows=predictors, outcome_rows=outcomes,
        evidence_identity="discovery:test",
    )
    candidate=Candidate.from_genome(
        family_id="MOMENTUM",
        genome={
            "momentum_feature":"return_20__v1","direction":"ABOVE",
            "threshold_quantile":0.5,"context_feature":"NONE",
            "context_threshold":0.5,"forward_horizon":5,
        },
        proposal_source="test",
    )
    result=evaluator.evaluate(candidate,evidence_identity="discovery:test")
    assert result.metrics["signal_count"] > 0
    assert result.metrics["mean_forward_return"] > 0
    assert result.metrics["search_fitness"] is not None
    assert result.analysis_refs


def test_analysis_evaluator_rejects_evidence_identity_mismatch():
    predictors,outcomes=_rows()
    evaluator=SearchCandidateAnalysisEvaluator.build(
        subject_id="equity:TEST", predictor_rows=predictors, outcome_rows=outcomes,
        evidence_identity="discovery:test",
    )
    candidate=Candidate.from_genome(
        family_id="MOMENTUM",
        genome={"momentum_feature":"return_20__v1","direction":"ABOVE","threshold_quantile":0.5,
                "context_feature":"NONE","context_threshold":0.5,"forward_horizon":5},
        proposal_source="test",
    )
    import pytest
    with pytest.raises(Exception):
        evaluator.evaluate(candidate,evidence_identity="other")
