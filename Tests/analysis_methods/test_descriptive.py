from Engines.Analysis.methods.descriptive import DescriptiveStatisticsMethod
from Engines.Analysis.methods.base import AnalysisServices
from Tests.analysis_methods.test_foundation import context


def test_descriptive_statistics_known_values():
    rows = [{"x":1.0},{"x":2.0},{"x":3.0},{"x":4.0}]
    c = context({"columns":["x"]})
    result = DescriptiveStatisticsMethod().execute(c, rows, AnalysisServices())
    x = result.scientific_result["columns"]["x"]
    assert x["mean"] == 2.5
    assert x["median"] == 2.5
    assert x["minimum"] == 1.0
    assert x["maximum"] == 4.0
    assert result.scientific_result["interpretation_boundary"] == "DESCRIPTIVE_ONLY"
