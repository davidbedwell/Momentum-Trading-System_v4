from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from MTS_V4.contracts import ResearchDecision
from MTS_V4.rd_codec import ResearchDecisionDecodeError
from MTS_V4.research_package_provider import ResearchPackageAwareResearchDirector
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.rp_appeal_provider import RPRepresentationAppellateResearchDirector


class RecordingAppeal:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.decision = ResearchDecision(
            continue_research=False,
            rp_id="rp:test",
            close_reason="appellate disposition",
        )

    def _request_decision(self, **kwargs):
        self.calls.append(dict(kwargs))
        return self.decision


class DecisionRepresentationAppealTests(unittest.TestCase):
    def _director(self, tmp: str, appeal: RecordingAppeal):
        return RPRepresentationAppellateResearchDirector(
            appeal=appeal,
            base_url="http://127.0.0.1:8000",
            model="test-primary-rd",
            api_key="",
            research_package_store=JsonResearchPackageStore(Path(tmp) / "research_packages"),
        )

    def test_three_failed_local_repairs_route_exact_final_defect_to_appeal(self):
        with tempfile.TemporaryDirectory() as tmp:
            appeal = RecordingAppeal()
            rd = self._director(tmp, appeal)
            first_failed_repair = ResearchDecisionDecodeError(
                "next_request missing required fields: ['subject_id']"
            )
            malformed_repairs = [
                json.dumps(
                    {
                        "continue_research": True,
                        "next_request": {},
                        "promote_findings": [],
                        "research_state": {},
                        "close_reason": None,
                    }
                ),
                json.dumps(
                    {
                        "continue_research": True,
                        "next_request": {"request_id": "r:3"},
                        "promote_findings": [],
                        "research_state": {},
                        "close_reason": None,
                    }
                ),
            ]
            with patch.object(
                ResearchPackageAwareResearchDirector,
                "_request_decision",
                side_effect=first_failed_repair,
            ), patch.object(rd, "_chat_completion", side_effect=malformed_repairs) as chat:
                decision = rd._request_decision(
                    operation="REPAIR_OBJECTIVE_CONTRACT",
                    mission="test mission",
                    payload={
                        "objective_execution_requirements": {
                            "decision_representation_repair_policy": "old policy"
                        },
                        "nexus_context": {"marker": "current-context"},
                    },
                )

        self.assertIs(decision, appeal.decision)
        self.assertEqual(chat.call_count, 2)
        self.assertEqual(len(appeal.calls), 1)
        appeal_payload = appeal.calls[0]["payload"]
        context = appeal_payload["nexus_context"]
        self.assertEqual(context["marker"], "current-context")
        self.assertEqual(
            context["ai_appeal"]["authority"],
            "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
        )
        self.assertEqual(
            context["ai_appeal"]["failure_layer"],
            "DECISION_REPRESENTATION",
        )
        self.assertEqual(
            context["ai_appeal"]["primary_representation_repairs_exhausted"],
            3,
        )
        self.assertIn(
            "subject_id",
            context["ai_appeal"]["objective_representation_defect"],
        )
        self.assertIn(
            "up to three representation repairs",
            appeal_payload["objective_execution_requirements"][
                "decision_representation_repair_policy"
            ],
        )

    def test_second_local_repair_can_return_valid_decision_without_appeal(self):
        with tempfile.TemporaryDirectory() as tmp:
            appeal = RecordingAppeal()
            rd = self._director(tmp, appeal)
            first_failed_repair = ResearchDecisionDecodeError(
                "next_request missing required fields: ['subject_id']"
            )
            valid_repair = json.dumps(
                {
                    "continue_research": False,
                    "next_request": None,
                    "promote_findings": [],
                    "research_state": {},
                    "close_reason": "local repair succeeded",
                }
            )
            with patch.object(
                ResearchPackageAwareResearchDirector,
                "_request_decision",
                side_effect=first_failed_repair,
            ), patch.object(rd, "_chat_completion", return_value=valid_repair) as chat:
                decision = rd._request_decision(
                    operation="INTERPRET_ANALYSIS_RESULT",
                    mission="test mission",
                    payload={"nexus_context": {}},
                )

        self.assertFalse(decision.continue_research)
        self.assertEqual(decision.close_reason, "local repair succeeded")
        self.assertEqual(chat.call_count, 1)
        self.assertEqual(appeal.calls, [])


if __name__ == "__main__":
    unittest.main()
