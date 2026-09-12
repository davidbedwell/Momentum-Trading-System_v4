from __future__ import annotations

import unittest

from MTS_V4.batch_contracts import BatchResearchDecision
from MTS_V4.rolling_program_state import (
    RollingProgramDisposition,
    RollingProgramStateError,
    rolling_program_instruction,
)


class RollingProgramStateTests(unittest.TestCase):
    def test_blind_validation_is_distinct_from_subject_completion(self):
        decision = BatchResearchDecision(
            continue_research=False,
            research_state={
                "rolling_program": {
                    "disposition": "RUN_BLIND_VALIDATION",
                    "hypothesis_id": "AMD-H001",
                    "rationale": "Freeze and test H001 before resuming exploration.",
                }
            },
            close_reason="Exploration phase pauses at a frozen validation boundary.",
        )
        instruction = rolling_program_instruction(decision)
        self.assertEqual(RollingProgramDisposition.RUN_BLIND_VALIDATION, instruction.disposition)
        self.assertEqual("AMD-H001", instruction.hypothesis_id)

    def test_awaiting_requires_no_active_batch(self):
        decision = BatchResearchDecision(
            continue_research=True,
            research_state={
                "rolling_program": {
                    "disposition": "AWAIT_NEW_EVIDENCE",
                    "hypothesis_id": "AMD-H001",
                    "rationale": "No unexposed observations currently available.",
                }
            },
        )
        with self.assertRaisesRegex(RollingProgramStateError, "requires continue_research=false"):
            rolling_program_instruction(decision)

    def test_resume_exploration_requires_an_executable_continuation(self):
        decision = BatchResearchDecision(
            continue_research=False,
            research_state={
                "rolling_program": {
                    "disposition": "RESUME_EXPLORATION",
                    "hypothesis_id": None,
                    "rationale": "Validation is complete.",
                }
            },
            close_reason="invalid fixture",
        )
        with self.assertRaisesRegex(RollingProgramStateError, "requires continue_research=true"):
            rolling_program_instruction(decision)


if __name__ == "__main__":
    unittest.main()
