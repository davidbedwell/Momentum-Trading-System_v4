from __future__ import annotations

from MTS_V4.analysis import ExactMethodAnalysisExecutor
from MTS_V4.contracts import AnalysisRequest, ResearchPhase
from MTS_V4.cross_sectional_analysis import analysis_method as rank_method
from MTS_V4.cross_sectional_association import analysis_method as association_method
from MTS_V4.cross_sectional_statistics import analysis_method as cohort_method
from MTS_V4.standard_methods import standard_analysis_methods


def _execute(executor, method_id, payloads, parameters):
    result = executor.execute(
        AnalysisRequest(
            request_id=f"request:{method_id}",
            subject_id="universe:synthetic",
            question="Synthetic mechanical operability proof.",
            method_id=method_id,
            evidence_ids=(),
            parameters=parameters,
            research_phase=ResearchPhase.EXPLORATION,
        ),
        payloads,
    )
    assert result.execution_metadata["execution_status"] == "SUCCESS"
    return result


def test_predictor_outcome_panel_can_execute_complete_cross_sectional_scientific_path():
    executor = ExactMethodAnalysisExecutor()
    for method in (*standard_analysis_methods(), rank_method(), association_method(), cohort_method()):
        executor.register(method)

    predictors = []
    outcomes = []
    for day in range(20):
        effective_date = f"2026-01-{day + 1:02d}"
        for security_index, security_id in enumerate(("A", "B", "C", "D", "E")):
            score = (security_index + 1) / 5
            predictors.append(
                {
                    "security_id": security_id,
                    "effective_date": effective_date,
                    "medium_term_return": score + day * 0.001,
                }
            )
            outcomes.append(
                {
                    "security_id": security_id,
                    "effective_date": effective_date,
                    "forward_return": score * 0.02 + day * 0.0001,
                }
            )

    composed = _execute(
        executor,
        "analysis.dataset.compose",
        {"predictors": predictors, "outcomes": tuple(reversed(outcomes))},
        {
            "alignment": [
                {"input_name": "predictors", "key": {"mode": "COLUMN", "columns": ["security_id", "effective_date"]}},
                {"input_name": "outcomes", "key": {"mode": "COLUMN", "columns": ["security_id", "effective_date"]}},
            ],
            "selections": [
                {"input_name": "predictors", "column": "security_id", "output_name": "security_id"},
                {"input_name": "predictors", "column": "effective_date", "output_name": "effective_date"},
                {"input_name": "predictors", "column": "medium_term_return", "output_name": "medium_term_return"},
                {"input_name": "outcomes", "column": "forward_return", "output_name": "forward_return"},
            ],
            "join_type": "INNER",
        },
    )
    joined = composed.outputs["derived_datasets"]["composed_dataset"]
    assert len(joined) == 100

    ranked = _execute(
        executor,
        "analysis.cross_sectional.rank",
        {"joined": joined},
        {
            "value_column": "medium_term_return",
            "output_column": "medium_term_rank",
            "group_by": ["effective_date"],
            "ascending": True,
        },
    )
    ranked_rows = ranked.outputs["derived_datasets"]["cross_sectional_ranked_dataset"]

    association = _execute(
        executor,
        "analysis.cross_sectional.association",
        {"ranked": ranked_rows},
        {
            "predictor_column": "medium_term_rank",
            "outcome_column": "forward_return",
            "date_column": "effective_date",
            "association_type": "spearman",
            "newey_west_max_lag": 3,
        },
    )
    assert association.outputs["equal_date_association"]["mean"] == 1.0
    assert association.outputs["equal_date_association"]["n_dates"] == 20

    cohort = _execute(
        executor,
        "analysis.cross_sectional.cohort_effect",
        {"ranked": ranked_rows},
        {
            "cohort_column": "medium_term_rank",
            "outcome_column": "forward_return",
            "threshold": 0.75,
            "direction": "GE",
            "date_column": "effective_date",
            "newey_west_max_lag": 3,
        },
    )
    assert cohort.outputs["equal_date_paired_difference"]["n_dates"] == 20
    assert cohort.outputs["equal_date_paired_difference"]["mean"] > 0
