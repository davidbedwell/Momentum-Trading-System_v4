from __future__ import annotations

import json
import unittest

from MTS_V4.rolling_validation_provider import RollingValidationSolBatchResearchDirector


class RollingValidationProviderTests(unittest.TestCase):
    def test_prompt_separates_hypothesis_identity_from_trial_identity(self):
        messages = RollingValidationSolBatchResearchDirector._batch_messages(
            operation="BEGIN_BATCH_RESEARCH",
            mission="test mission",
            payload={},
        )
        system = messages[0]["content"]
        user = json.loads(messages[1]["content"])
        instructions = "\n".join(user["instructions"])

        self.assertIn("repeated blind tests are trials of that same hypothesis", system)
        self.assertIn("H001-T01", system)
        self.assertIn("does not terminate research on its subject", system)
        self.assertIn("Never relabel previously exposed exploratory history as blind", system)
        self.assertIn("resume unrestricted exploration", system)
        self.assertIn("do not create a new hypothesis_id for each replication", instructions)
        self.assertIn("permanently exposed", instructions)


if __name__ == "__main__":
    unittest.main()
