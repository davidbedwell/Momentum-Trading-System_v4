from __future__ import annotations

import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from MTS_V4.contracts import EvidenceMetadata, SubjectMetadata
from MTS_V4.nexus import InMemoryResearchNexus, NexusError
from MTS_V4.nexus_json import JsonResearchNexus


class EvidenceReacquisitionNexusTests(unittest.TestCase):
    @staticmethod
    def _first() -> EvidenceMetadata:
        return EvidenceMetadata(
            evidence_id="evidence:equity:AAPL:stable",
            subject_id="equity:AAPL",
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2026-01-01",
            coverage_end="2026-01-02",
            row_count=2,
            schema=("date", "close"),
            provenance={
                "vendor": "fixture",
                "scope": "ticker",
                "acquired_at_utc": "2026-09-07T20:00:00Z",
            },
            neutral_semantics="Observed price path.",
            content_identity="sha256:stable-content",
        )

    def _exercise(self, nexus) -> None:
        nexus.upsert_subject(SubjectMetadata(subject_id="equity:AAPL", ticker="AAPL"))
        first = self._first()
        nexus.upsert_evidence_metadata(first)

        reacquired = replace(
            first,
            provenance={
                "vendor": "fixture",
                "scope": "ticker",
                "acquired_at_utc": "2026-09-07T21:00:00Z",
            },
        )
        nexus.upsert_evidence_metadata(reacquired)

        # The old durable record is preserved rather than overwritten by the
        # newer acquisition clock.
        stored = nexus.get_evidence_metadata(first.evidence_id)
        self.assertEqual(
            stored.provenance["acquired_at_utc"],
            "2026-09-07T20:00:00Z",
        )

        # Scientifically/source-meaningful metadata still cannot be changed
        # behind an existing evidence identity.
        changed_source_metadata = replace(
            first,
            provenance={
                "vendor": "different-vendor",
                "scope": "ticker",
                "acquired_at_utc": "2026-09-07T22:00:00Z",
            },
        )
        with self.assertRaisesRegex(NexusError, "different metadata"):
            nexus.upsert_evidence_metadata(changed_source_metadata)

        changed_content = replace(first, content_identity="sha256:different-content")
        with self.assertRaisesRegex(NexusError, "different metadata"):
            nexus.upsert_evidence_metadata(changed_content)

    def test_in_memory_nexus_accepts_clock_only_reacquisition_without_overwrite(self):
        self._exercise(InMemoryResearchNexus())

    def test_json_nexus_accepts_clock_only_reacquisition_without_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nexus.json"
            self._exercise(JsonResearchNexus(path))
            reopened = JsonResearchNexus(path)
            self.assertEqual(
                reopened.get_evidence_metadata(self._first().evidence_id).provenance[
                    "acquired_at_utc"
                ],
                "2026-09-07T20:00:00Z",
            )


if __name__ == "__main__":
    unittest.main()
