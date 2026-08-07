from Engines.Analysis.methods.comparison import CohortOutcomeComparisonMethod
from Engines.Analysis.methods.base import AnalysisServices
from Tests.analysis_methods.test_foundation import context


def test_cohort_comparison_known_difference():
    rows = [
        {"group":"A","ret":1.0},{"group":"A","ret":3.0},
        {"group":"B","ret":5.0},{"group":"B","ret":7.0},
    ]
    c = context({"group_column":"group","outcome_column":"ret"})
    method = CohortOutcomeComparisonMethod()
    result = method.execute(c, rows, AnalysisServices())
    assert result.scientific_result["groups"]["A"]["mean"] == 2.0
    assert result.scientific_result["groups"]["B"]["mean"] == 6.0
    assert result.scientific_result["pairwise_mean_differences"][0]["mean_difference"] == -4.0
    assert method.validate(result, c).passed
