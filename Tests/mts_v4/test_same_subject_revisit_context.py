from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.research_package_store import JsonResearchPackageStore
from MTS_V4.sol_batch_provider import SolBatchResearchDirector
from MTS_V4.subject_scientific_context import (
    SubjectContextSolBatchResearchDirector,
    load_same_subject_prior_science,
    load_subject_scientific_context,
)


def _write_package(path: Path, *, subject_id: str, findings: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "format": JsonResearchPackageStore.FORMAT,
                "research_package": {
                    "rp_id": f"RP-{subject_id.split(':')[-1]}",
                    "campaign_id": "historical-campaign",
                    "subject_id": subject_id,
                    "status": "CLOSED",
                    "originating_question": "What did the shorter window show?",
                    "originating_rationale": "Preserve prior exploratory science.",
                    "hypotheses": [{"statement": "tentative"}],
                    "predictive_hypotheses": [{"hypothesis_id": "ph-1"}],
                    "findings": findings,
                    "unresolved_issues": [{"issue": "regime dependence"}],
                    "analyses": [{"payload": {"rows": [1, 2, 3]}, "cache_key": "forbidden"}],
                    "close_reason": "short window exhausted",
                    "final_assessment": "historical assessment",
                },
            }
        ),
        encoding="utf-8",
    )


def _write_nexus(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "format": "MTS_V4_RESEARCH_NEXUS_V1",
                "subjects": [{"subject_id": "equity:XOM", "ticker": "XOM"}],
                "evidence_metadata": [],
                "analysis_result_metadata": [],
                "findings": [
                    {
                        "finding_id": "finding-in-package",
                        "subject_id": "equity:XOM",
                        "statement": "already represented by its package",
                        "supporting_result_ids": [],
                        "evidence_ids": [],
                        "metadata": {},
                    },
                    {
                        "finding_id": "nexus-only",
                        "subject_id": "equity:XOM",
                        "statement": "promoted only to Nexus",
                        "supporting_result_ids": [],
                        "evidence_ids": [],
                        "metadata": {"status": "exploratory"},
                    },
                    {
                        "finding_id": "retracted",
                        "subject_id": "equity:XOM",
                        "statement": "must not be exposed",
                        "supporting_result_ids": [],
                        "evidence_ids": [],
                        "metadata": {},
                    },
                ],
                "finding_retractions": [
                    {
                        "finding_id": "retracted",
                        "reason": "withdrawn",
                        "initiated_by": "test",
                        "retracted_at_utc": "2026-09-12T00:00:00+00:00",
                        "replacement_finding_id": None,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


class SameSubjectRevisitContextTests(unittest.TestCase):
    def test_loader_unions_package_science_with_nexus_only_active_findings(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _write_package(
                root / "mts-v4-old-xom" / "research_packages" / "RP-XOM.json",
                subject_id="equity:XOM",
                findings=[{"finding_id": "finding-in-package", "statement": "package copy"}],
            )
            _write_package(
                root / "mts-v4-old-amd" / "research_packages" / "RP-AMD.json",
                subject_id="equity:AMD",
                findings=[{"finding_id": "amd-finding"}],
            )
            _write_nexus(root / "mts-v4-old-xom" / "research_nexus.json")

            context = load_same_subject_prior_science(root, active_subject_id="equity:XOM")

            self.assertEqual(context["subject_id"], "equity:XOM")
            self.assertEqual(len(context["research_packages"]), 1)
            package = context["research_packages"][0]
            self.assertEqual(package["originating_question"], "What did the shorter window show?")
            self.assertEqual(package["predictive_hypotheses"][0]["hypothesis_id"], "ph-1")
            self.assertNotIn("analyses", package)
            serialized = json.dumps(context)
            self.assertNotIn("cache_key", serialized)
            self.assertNotIn('"rows"', serialized)

            nexus_findings = context["nexus_only_findings"]
            self.assertEqual([item["finding_id"] for item in nexus_findings], ["nexus-only"])
            self.assertEqual(nexus_findings[0]["status"], "ACTIVE")
            self.assertIn("research_nexus.json", nexus_findings[0]["source_path"])
            self.assertFalse(context["policy"]["deterministic_scientific_ranking"])
            self.assertFalse(context["policy"]["mandatory_retest_agenda"])

    def test_same_subject_context_is_opt_in(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            memory_path = root / "mts-v4-memory" / "cross_subject_memory.json"
            memory_path.parent.mkdir(parents=True)
            memory_path.write_text(
                json.dumps({"schema_version": 1, "records": [], "frontier": None}),
                encoding="utf-8",
            )
            _write_package(
                root / "mts-v4-old-xom" / "research_packages" / "RP-XOM.json",
                subject_id="equity:XOM",
                findings=[],
            )

            normal = load_subject_scientific_context(root, active_subject_id="equity:XOM")
            revisit = load_subject_scientific_context(
                root,
                active_subject_id="equity:XOM",
                include_same_subject_prior_science=True,
            )

            self.assertIsNone(normal.same_subject_prior_science)
            self.assertEqual(len(revisit.same_subject_prior_science["research_packages"]), 1)

    def test_rd_payload_omits_field_normally_and_adds_it_for_revisit(self) -> None:
        subject = SubjectMetadata(subject_id="equity:XOM", ticker="XOM")
        common = dict(subject=subject, evidence=(), available_methods=(), nexus_context={})
        with patch.object(SolBatchResearchDirector, "_batch_common_payload", return_value={}):
            normal = object.__new__(SubjectContextSolBatchResearchDirector)
            normal._prior_subject_scientific_context = {"subjects": []}
            normal._same_subject_prior_scientific_context = None
            self.assertNotIn("same_subject_prior_science", normal._batch_common_payload(**common))

            revisit = object.__new__(SubjectContextSolBatchResearchDirector)
            revisit._prior_subject_scientific_context = {"subjects": []}
            revisit._same_subject_prior_scientific_context = {"subject_id": "equity:XOM"}
            payload = revisit._batch_common_payload(**common)
            self.assertEqual(payload["same_subject_prior_science"]["subject_id"], "equity:XOM")


if __name__ == "__main__":
    unittest.main()
