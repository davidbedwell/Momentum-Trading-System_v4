from __future__ import annotations

from typing import Mapping

from .cross_subject_memory import CrossSubjectScientificMemory


def build_cross_subject_context(
    scientific_memory: CrossSubjectScientificMemory | None,
    *,
    active_subject_id: str,
) -> Mapping[str, object]:
    """Return compact prior-subject scientific context for RD.

    The active subject is excluded so this context remains specifically
    cross-subject. Existing subject-local Nexus/RP context remains separate.
    """

    if scientific_memory is None:
        return {
            "records": [],
            "frontier": None,
            "policy": {
                "authority": "RD_AUTHORED_SCIENTIFIC_CONTEXT",
                "raw_rows_present": False,
                "mandatory_research_agenda": False,
                "rd_may_test_challenge_reformulate_condition_defer_or_ignore": True,
                "deterministic_scientific_ranking": False,
            },
        }
    context_method = getattr(scientific_memory, "context", None)
    if callable(context_method):
        return context_method(exclude_subject_id=active_subject_id)
    return {
        "records": [
            record.compact_context()
            for record in scientific_memory.records()
            if record.subject_id != active_subject_id
        ],
        "frontier": (
            scientific_memory.frontier().compact_context()
            if scientific_memory.frontier() is not None
            else None
        ),
        "policy": {
            "authority": "RD_AUTHORED_SCIENTIFIC_CONTEXT",
            "raw_rows_present": False,
            "mandatory_research_agenda": False,
            "rd_may_test_challenge_reformulate_condition_defer_or_ignore": True,
            "deterministic_scientific_ranking": False,
        },
    }
