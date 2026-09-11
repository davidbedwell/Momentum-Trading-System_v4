import pytest

from MTS_V4.cross_subject_memory import ResearchFrontierState, ScientificMemoryRecord
from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore


def _record(record_id: str, summary: str) -> ScientificMemoryRecord:
    return ScientificMemoryRecord(
        record_id=record_id,
        subject_id="AAPL",
        kind="METHOD_LESSON",
        summary=summary,
    )


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


def test_publish_batch_rejects_internal_record_id_conflict_without_partial_write(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    store = JsonCrossSubjectScientificMemoryStore(path)

    with pytest.raises(ValueError, match="batch contains record_id with different content"):
        store.publish_batch(
            (
                _record("coordinate-lineage-lesson:v1", "first Sol statement"),
                _record("coordinate-lineage-lesson:v1", "different Sol statement"),
            )
        )

    assert store.records() == ()
    assert not path.exists()


def test_publish_batch_rejects_conflict_with_durable_memory_without_partial_batch_write(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    store = JsonCrossSubjectScientificMemoryStore(path)
    durable = _record("coordinate-lineage-lesson:v1", "durable Sol statement")
    store.publish(durable)
    before = path.read_text(encoding="utf-8")

    with pytest.raises(ValueError, match="already exists with different content"):
        store.publish_batch(
            (
                _record("new-record:v1", "must not be partially written"),
                _record("coordinate-lineage-lesson:v1", "conflicting Sol statement"),
            )
        )

    assert store.records() == (durable,)
    assert path.read_text(encoding="utf-8") == before


def test_publish_batch_treats_exact_duplicate_as_idempotent(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    store = JsonCrossSubjectScientificMemoryStore(path)
    record = _record("coordinate-lineage-lesson:v1", "same Sol statement")

    store.publish_batch((record, record))
    reopened = JsonCrossSubjectScientificMemoryStore(path)

    assert reopened.records() == (record,)
