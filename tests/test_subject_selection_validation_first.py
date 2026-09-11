import json

from MTS_V4.adaptive_batch import SubjectEligibilityEnvelope
from MTS_V4.cross_subject_memory import InMemoryCrossSubjectScientificMemory
from MTS_V4.subject_selection import SolAdaptiveSubjectSelector


class StubRD:
    def __init__(self, response):
        self.response = response

    def _chat_completion(self, messages):
        return self.response


def test_sol_may_choose_validation_first_for_existing_hypothesis():
    selector = SolAdaptiveSubjectSelector(
        rd=StubRD(
            json.dumps(
                {
                    "subject_id": "MSFT",
                    "rationale": "Useful unseen discriminator for the prior rebound hypothesis.",
                    "mode": "VALIDATION_FIRST",
                    "hypothesis_id": "H-AAPL-MOM-001-SEVERE-5D-REBOUND",
                }
            )
        ),
        scientific_memory=InMemoryCrossSubjectScientificMemory(),
        eligibility=SubjectEligibilityEnvelope(),
    )
    decision = selector.choose_next(
        mission="predict T+1 onward",
        previously_seen=("AAPL",),
        candidate_subject_ids=("MSFT", "XOM"),
    )
    assert decision.subject_id == "MSFT"
    assert decision.mode == "VALIDATION_FIRST"
    assert decision.hypothesis_id == "H-AAPL-MOM-001-SEVERE-5D-REBOUND"
