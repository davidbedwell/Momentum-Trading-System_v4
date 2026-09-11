from MTS_V4.cross_subject_context import build_cross_subject_context
from MTS_V4.cross_subject_memory import InMemoryCrossSubjectScientificMemory, ScientificMemoryRecord


def test_cross_subject_context_excludes_active_subject():
    memory = InMemoryCrossSubjectScientificMemory()
    memory.publish(ScientificMemoryRecord(record_id="a", subject_id="AAPL", kind="K", summary="a"))
    memory.publish(ScientificMemoryRecord(record_id="m", subject_id="MSFT", kind="K", summary="m"))
    context = build_cross_subject_context(memory, active_subject_id="MSFT")
    assert [item["subject_id"] for item in context["records"]] == ["AAPL"]
