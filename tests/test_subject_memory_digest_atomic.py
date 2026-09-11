import json

import pytest

from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor


class FakeRD:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def _chat_completion(self, messages):
        self.calls.append(messages)
        if not self.responses:
            raise AssertionError("unexpected extra RD call")
        return json.dumps(self.responses.pop(0))


def _conflicting_response():
    return {
        "records": [
            {
                "record_id": "xsm:equity:AAPL:coordinate-lineage-lesson:v1",
                "kind": "METHOD_LESSON",
                "summary": "first statement",
                "result_ids": [],
                "evidence_ids": [],
                "metadata": {},
            },
            {
                "record_id": "xsm:equity:AAPL:coordinate-lineage-lesson:v1",
                "kind": "METHOD_LESSON",
                "summary": "different statement",
                "result_ids": [],
                "evidence_ids": [],
                "metadata": {},
            },
        ],
        "frontier": {
            "summary": "would have been frontier v1",
            "open_questions": [],
            "candidate_generalizations": [],
            "contradictions": [],
            "deprioritized_avenues": [],
            "missing_resources": [],
            "source_record_ids": [],
        },
    }


def _repaired_response():
    return {
        "records": [
            {
                "record_id": "xsm:equity:AAPL:coordinate-lineage-lesson:v1",
                "kind": "METHOD_LESSON",
                "summary": "resolved statement",
                "result_ids": [],
                "evidence_ids": [],
                "metadata": {},
            }
        ],
        "frontier": {
            "summary": "frontier v1",
            "open_questions": [],
            "candidate_generalizations": [],
            "contradictions": [],
            "deprioritized_avenues": [],
            "missing_resources": [],
            "source_record_ids": ["xsm:equity:AAPL:coordinate-lineage-lesson:v1"],
        },
    }


def test_subject_memory_digest_repairs_conflicting_duplicate_ids_before_persist(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    memory = JsonCrossSubjectScientificMemoryStore(path)
    rd = FakeRD([_conflicting_response(), _repaired_response()])
    author = SolSubjectScientificMemoryAuthor(rd=rd, scientific_memory=memory)

    digest = author.author_and_persist(
        mission="test",
        subject_id="equity:AAPL",
        subject_scientific_context={"test": True},
    )

    assert len(rd.calls) == 2
    repair_message = json.loads(rd.calls[1][-1]["content"])
    assert repair_message["operation"] == "REPAIR_CROSS_SUBJECT_SCIENTIFIC_MEMORY_REPRESENTATION"
    assert "batch contains record_id with different content" in repair_message["objective_defect"]
    assert len(digest.records) == 1
    assert memory.records() == digest.records
    assert memory.frontier() == digest.frontier
    assert path.exists()


def test_subject_memory_digest_exhausted_repairs_persist_nothing(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    memory = JsonCrossSubjectScientificMemoryStore(path)
    rd = FakeRD([_conflicting_response()] * 4)
    author = SolSubjectScientificMemoryAuthor(rd=rd, scientific_memory=memory)

    with pytest.raises(ValueError, match="representation repair exhausted after 3 repairs"):
        author.author_and_persist(
            mission="test",
            subject_id="equity:AAPL",
            subject_scientific_context={"test": True},
        )

    assert len(rd.calls) == 4
    assert memory.records() == ()
    assert memory.frontier() is None
    assert not path.exists()
