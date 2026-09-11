from MTS_V4.cross_subject_memory import ResearchFrontierState, ScientificMemoryRecord
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore


def test_cross_subject_memory_store_round_trips(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    store = JsonCrossSubjectScientificMemoryStore(path)
    store.publish(
        ScientificMemoryRecord(
            record_id="m1",
            subject_id="AAPL",
            kind="TENTATIVE_HYPOTHESIS",
            summary="severe weakness rebound candidate",
            hypothesis_id="H-AAPL-1",
            status="TENTATIVE",
        )
    )
    store.set_frontier(
        ResearchFrontierState(
            version=1,
            summary="test whether severe weakness rebound generalizes",
            source_record_ids=("m1",),
        )
    )

    reopened = JsonCrossSubjectScientificMemoryStore(path)
    assert reopened.records()[0].subject_id == "AAPL"
    assert reopened.frontier() is not None
    assert reopened.frontier().version == 1
    text = path.read_text(encoding="utf-8")
    assert '"contains_raw_rows": false' in text
    assert '"contains_reusable_analysis_payloads": false' in text
