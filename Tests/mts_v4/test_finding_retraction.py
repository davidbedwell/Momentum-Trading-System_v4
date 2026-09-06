from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from MTS_V4.contracts import Finding, SubjectMetadata
from MTS_V4.nexus import InMemoryResearchNexus, NexusError
from MTS_V4.nexus_json import JsonResearchNexus


class FindingRetractionTests(unittest.TestCase):
    def _finding(self) -> Finding:
        return Finding(
            finding_id="f:contaminated",
            subject_id="AAPL",
            statement="Scientifically contaminated smoke finding",
            supporting_result_ids=("analysis-result:5",),
            evidence_ids=("evidence:equity:AAPL:1",),
            metadata={"test_artifact": True},
        )

    def test_in_memory_retraction_excludes_finding_from_active_retrieval(self):
        nexus = InMemoryResearchNexus()
        nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
        nexus.publish_finding(self._finding())

        retraction = nexus.retract_finding(
            "f:contaminated",
            reason="Derived-data lineage defect invalidated the scientific interpretation.",
            initiated_by="human:owner",
        )

        self.assertEqual(retraction.finding_id, "f:contaminated")
        self.assertEqual(retraction.initiated_by, "human:owner")
        self.assertIsNone(nexus.get_finding("f:contaminated"))
        self.assertEqual(nexus.findings_for_subject("AAPL"), ())
        self.assertEqual(
            nexus.get_finding_retraction("f:contaminated").reason,
            "Derived-data lineage defect invalidated the scientific interpretation.",
        )
        self.assertEqual(nexus.snapshot_metadata()["findings"], 1)
        self.assertEqual(nexus.snapshot_metadata()["finding_retractions"], 1)
        self.assertEqual(nexus.snapshot_metadata()["active_findings"], 0)

    def test_json_retraction_survives_reopen_and_preserves_original_for_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nexus.json"
            nexus = JsonResearchNexus(path)
            nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
            nexus.publish_finding(self._finding())
            nexus.retract_finding(
                "f:contaminated",
                reason="Smoke-test contamination discovered after campaign close.",
                initiated_by="human:owner",
            )

            reopened = JsonResearchNexus(path)
            self.assertIsNone(reopened.get_finding("f:contaminated"))
            self.assertEqual(reopened.findings_for_subject("AAPL"), ())
            self.assertEqual(
                reopened.get_finding_retraction("f:contaminated").initiated_by,
                "human:owner",
            )

            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(len(document["findings"]), 1)
            self.assertEqual(document["findings"][0]["finding_id"], "f:contaminated")
            self.assertEqual(len(document["finding_retractions"]), 1)
            self.assertEqual(
                document["finding_retractions"][0]["finding_id"],
                "f:contaminated",
            )

    def test_retraction_requires_explicit_reason_and_initiator(self):
        nexus = InMemoryResearchNexus()
        nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
        nexus.publish_finding(self._finding())

        with self.assertRaises(NexusError):
            nexus.retract_finding(
                "f:contaminated",
                reason="",
                initiated_by="human:owner",
            )
        with self.assertRaises(NexusError):
            nexus.retract_finding(
                "f:contaminated",
                reason="contaminated",
                initiated_by="",
            )

    def test_retracted_finding_id_cannot_be_republished(self):
        nexus = InMemoryResearchNexus()
        nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
        nexus.publish_finding(self._finding())
        nexus.retract_finding(
            "f:contaminated",
            reason="contaminated",
            initiated_by="human:owner",
        )

        with self.assertRaises(NexusError):
            nexus.publish_finding(self._finding())


if __name__ == "__main__":
    unittest.main()
