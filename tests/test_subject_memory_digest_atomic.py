import json

import pytest

from MTS_V4.cross_subject_memory_store import JsonCrossSubjectScientificMemoryStore
from MTS_V4.subject_memory_digest import SolSubjectScientificMemoryAuthor


class FakeRD:
    def __init__(self, response):
        self.response = response

    def _chat_completion(self, _messages):
        return json.dumps(self.response)


def test_subject_memory_digest_conflicting_duplicate_ids_persist_nothing(tmp_path):
    path = tmp_path / "cross_subject_memory.json"
    memory = JsonCrossSubjectScientificMemoryStore(path)
    rd = FakeRD(
        {
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
    )
    author = SolSubjectScientificMemoryAuthor(rd=rd, scientific_memory=memory)

    with pytest.raises(ValueError, match="batch contains record_id with different content"):
        author.author_and_persist(
            mission="test",
            subject_id="equity:AAPL",
            subject_scientific_context={"test": True},
        )

    assert memory.records() == ()
    assert memory.frontier() is None
    assert not path.exists()
