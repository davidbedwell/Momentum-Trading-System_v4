import pytest

from Engines.Analysis.methods.relationship import RelationshipRedundancyMethod
from Engines.Analysis.methods.base import AnalysisServices
from Tests.analysis_methods.test_foundation import context


def test_pearson_detects_known_perfect_relationship():
    rows = [{"x":1,"y":2},{"x":2,"y":4},{"x":3,"y":6},{"x":4,"y":8}]
    c = context({"columns":["x","y"],"correlation_type":"pearson"})
    result = RelationshipRedundancyMethod().execute(c, rows, AnalysisServices())
    assert result.scientific_result["pairs"][0]["correlation"] == pytest.approx(1.0)
    assert result.scientific_result["interpretation_boundary"] == "RELATIONSHIP_NOT_CAUSATION"


def test_spearman_handles_monotonic_nonlinear_relationship():
    rows = [{"x":1,"y":1},{"x":2,"y":4},{"x":3,"y":9},{"x":4,"y":16}]
    c = context({"columns":["x","y"],"correlation_type":"spearman"})
    result = RelationshipRedundancyMethod().execute(c, rows, AnalysisServices())
    assert result.scientific_result["pairs"][0]["correlation"] == pytest.approx(1.0)
