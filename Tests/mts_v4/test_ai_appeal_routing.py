from __future__ import annotations

import unittest

from MTS_V4.appeal_provider import AppellateResearchDirector
from MTS_V4.contracts import ContractDefect, ResearchDecision, SubjectMetadata


class RecordingProvider:
    def __init__(self, decision: ResearchDecision) -> None:
        self.decision = decision
        self.repair_calls: list[dict[str, object]] = []

    def begin_research(self, **kwargs):
        return self.decision

    def resume_research(self, **kwargs):
        return self.decision

    def repair_request(self, **kwargs):
        self.repair_calls.append(dict(kwargs))
        return self.decision

    def interpret_result(self, **kwargs):
        return self.decision


class AppellateResearchDirectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.subject = SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL")
        self.decision = ResearchDecision(continue_research=True, rp_id="rp:test")
        self.defects = (ContractDefect(code="BAD_INPUT", message="objective defect"),)
        self.primary = RecordingProvider(self.decision)
        self.appeal = RecordingProvider(self.decision)
        self.rd = AppellateResearchDirector(
            primary=self.primary,
            appeal=self.appeal,
            primary_repair_attempts=3,
        )

    def _repair(self) -> ResearchDecision:
        return self.rd.repair_request(
            mission="test mission",
            subject=self.subject,
            prior_decision=self.decision,
            defects=self.defects,
            evidence=(),
            available_methods=(),
            nexus_context={"marker": "current-context"},
        )

    def test_three_primary_repairs_then_routes_next_repair_to_appeal(self):
        self._repair()
        self._repair()
        self._repair()

        self.assertEqual(len(self.primary.repair_calls), 3)
        self.assertEqual(len(self.appeal.repair_calls), 0)

        self._repair()

        self.assertEqual(len(self.primary.repair_calls), 3)
        self.assertEqual(len(self.appeal.repair_calls), 1)
        appeal_context = self.appeal.repair_calls[0]["nexus_context"]
        self.assertEqual(appeal_context["marker"], "current-context")
        self.assertEqual(
            appeal_context["ai_appeal"]["authority"],
            "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
        )
        self.assertEqual(
            appeal_context["ai_appeal"]["primary_repair_attempts_exhausted"],
            3,
        )
        self.assertEqual(
            len(appeal_context["ai_appeal"]["failed_primary_repair_sequence"]),
            3,
        )

    def test_new_scientific_turn_resets_primary_repair_sequence(self):
        for _ in range(4):
            self._repair()
        self.assertEqual(len(self.appeal.repair_calls), 1)

        self.rd.begin_research(
            mission="test mission",
            subject=self.subject,
            evidence=(),
            available_methods=(),
            nexus_context={},
        )
        self._repair()

        self.assertEqual(len(self.primary.repair_calls), 4)
        self.assertEqual(len(self.appeal.repair_calls), 1)


if __name__ == "__main__":
    unittest.main()
