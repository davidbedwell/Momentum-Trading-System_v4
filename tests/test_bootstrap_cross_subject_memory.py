from __future__ import annotations

from MTS_V4.bootstrap import build_runtime
from MTS_V4.cross_subject_memory import InMemoryCrossSubjectScientificMemory
from MTS_V4.cross_subject_orchestrator import CrossSubjectResearchLoopOrchestrator


class _RD:
    def begin_research(self, **kwargs):
        raise AssertionError("not used")

    def resume_research(self, **kwargs):
        raise AssertionError("not used")

    def repair_request(self, **kwargs):
        raise AssertionError("not used")

    def interpret_result(self, **kwargs):
        raise AssertionError("not used")


def test_build_runtime_uses_cross_subject_orchestrator_when_memory_supplied():
    memory = InMemoryCrossSubjectScientificMemory()
    runtime = build_runtime(rd=_RD(), scientific_memory=memory)
    assert isinstance(runtime.orchestrator, CrossSubjectResearchLoopOrchestrator)


def test_build_runtime_preserves_subject_local_orchestrator_without_memory():
    runtime = build_runtime(rd=_RD())
    assert not isinstance(runtime.orchestrator, CrossSubjectResearchLoopOrchestrator)
