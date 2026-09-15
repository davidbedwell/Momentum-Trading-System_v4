from MTS_V4.analysis import RegisteredAnalysisMethod
from MTS_V4.cached_analysis import CachedLineageAwareAnalysisExecutor
from MTS_V4.contracts import AnalysisRequest, ResearchPhase


def test_identical_analysis_spec_reuses_result_but_preserves_new_request_lineage():
    calls = {"count": 0}

    def method(payloads, parameters):
        calls["count"] += 1
        return {"value": parameters["value"]}

    executor = CachedLineageAwareAnalysisExecutor()
    executor.register(RegisteredAnalysisMethod("test.method", method))
    base = dict(
        subject_id="universe:test",
        question="q",
        method_id="test.method",
        evidence_ids=("e1",),
        parameters={"value": 7},
        research_phase=ResearchPhase.EXPLORATION,
    )
    first = executor.execute(AnalysisRequest(request_id="r1", **base), {"e1": ({"x": 1},)})
    second = executor.execute(AnalysisRequest(request_id="r2", **base), {"e1": ({"x": 1},)})
    assert calls["count"] == 1
    assert first.result_id != second.result_id
    assert second.request_id == "r2"
    assert second.execution_metadata["deterministic_cache_hit"] is True
