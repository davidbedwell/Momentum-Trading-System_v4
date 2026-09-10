from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from MTS_V4.contracts import ResearchDecision
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


class RPRepresentationAppealTests(unittest.TestCase):
    def test_exhausted_primary_representation_repairs_route_to_appeal(self):
        with tempfile.TemporaryDirectory() as tmp:
            appeal = RecordingAppeal()
            rd = RPRepresentationAppellateResearchDirector(
                appeal=appeal,
                research_package_store=JsonResearchPackageStore(Path(tmp) / "research_packages"),
            )
            exhausted = ValueError(
                "research package representation repair budget exhausted: "
                "parent_rp_id may not equal rp_id"
            )
            with patch.object(
                ResearchPackageAwareResearchDirector,
                "_request_decision",
                side_effect=exhausted,
            ):
                decision = rd._request_decision(
                    operation="INTERPRET_ANALYSIS_RESULT",
                    mission="test mission",
                    payload={"nexus_context": {"marker": "current-context"}},
                )

        self.assertIs(decision, appeal.decision)
        self.assertEqual(len(appeal.calls), 1)
        context = appeal.calls[0]["payload"]["nexus_context"]
        self.assertEqual(context["marker"], "current-context")
        self.assertEqual(
            context["ai_appeal"]["authority"],
            "AUTHORIZED_AI_SCIENTIFIC_APPEAL",
        )
        self.assertEqual(
            context["ai_appeal"]["failure_layer"],
            "RESEARCH_PACKAGE_REPRESENTATION",
        )
        self.assertEqual(
            context["ai_appeal"]["primary_representation_repairs_exhausted"],
            3,
        )
        self.assertEqual(
            context["ai_appeal"]["objective_representation_defect"],
            "parent_rp_id may not equal rp_id",
        )

    def test_unrelated_value_error_is_not_escalated(self):
        with tempfile.TemporaryDirectory() as tmp:
            appeal = RecordingAppeal()
            rd = RPRepresentationAppellateResearchDirector(
                appeal=appeal,
                research_package_store=JsonResearchPackageStore(Path(tmp) / "research_packages"),
            )
            with patch.object(
                ResearchPackageAwareResearchDirector,
                "_request_decision",
                side_effect=ValueError("unrelated failure"),
            ):
                with self.assertRaisesRegex(ValueError, "unrelated failure"):
                    rd._request_decision(
                        operation="BEGIN_RESEARCH",
                        mission="test mission",
                        payload={},
                    )

        self.assertEqual(appeal.calls, [])


if __name__ == "__main__":
    unittest.main()
