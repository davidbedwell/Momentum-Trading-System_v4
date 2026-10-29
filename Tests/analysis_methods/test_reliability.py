import pytest

from Engines.Analysis.methods.reliability import BasicStatisticalReliabilityMethod
from Engines.Analysis.methods.base import AnalysisServices
from Tests.analysis_methods.test_foundation import context


def test_basic_reliability_reports_mean_standard_error_and_ci():
    rows = [{"x":1.0},{"x":2.0},{"x":3.0},{"x":4.0}]
    c = context({"column":"x","confidence_level":0.95})
    method = BasicStatisticalReliabilityMethod()
    result = method.execute(c, rows, AnalysisServices())
    out = result.scientific_result
    assert out["n"] == 4
    assert out["mean"] == 2.5
    assert out["standard_error"] is not None
    assert out["normal_approximation_mean_ci"]["lower"] < 2.5
    assert out["normal_approximation_mean_ci"]["upper"] > 2.5
    assert method.validate(result, c).passed


def test_reliability_rejects_too_small_output_at_validation():
    c = context({"column":"x"})
    method = BasicStatisticalReliabilityMethod()
    result = method.execute(c, [{"x":1.0}], AnalysisServices())
    assert not method.validate(result, c).passed
