from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from MTS_V4.cache import TemporaryResearchCache
from MTS_V4.contracts import EvidenceMetadata, Finding, SubjectMetadata
from MTS_V4.intake import IntakeEngine, IntakePayload
from MTS_V4.nexus_json import JsonResearchNexus


class _Source:
    def acquire(self, subject):
        yield IntakePayload(
            payload=[{"date": "2026-01-01", "close": 100.0, "volume": 10}],
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="fixture-source",
            coverage_start="2026-01-01",
            coverage_end="2026-01-01",
            row_count=1,
            schema=("date", "close", "volume"),
            provenance={"vendor": "fixture"},
            neutral_semantics="Observed price path and aggregate volume; no participant intent is inferred.",
        )


class V4DataBoundaryTests(unittest.TestCase):
    def test_intake_stages_payload_in_temporary_cache_only(self):
        cache = TemporaryResearchCache()
        intake = IntakeEngine(cache)
        subject = SubjectMetadata(subject_id="AAPL", ticker="AAPL")
        descriptors = intake.ingest(subject=subject, source=_Source())
        self.assertEqual(len(descriptors), 1)
        descriptor = descriptors[0]
        self.assertEqual(descriptor.evidence_type, "OHLCV")
        self.assertEqual(cache.get(descriptor.cache_key)[0]["close"], 100.0)
        self.assertFalse(hasattr(descriptor, "payload"))
        durable = descriptor.durable_metadata()
        self.assertFalse(hasattr(durable, "cache_key"))

    def test_json_nexus_persists_ticker_evidence_metadata_and_findings_not_raw_dataset(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nexus.json"
            nexus = JsonResearchNexus(path)
            nexus.upsert_subject(SubjectMetadata(subject_id="AAPL", ticker="AAPL"))
            nexus.upsert_evidence_metadata(
                EvidenceMetadata(
                    evidence_id="ev:1",
                    subject_id="AAPL",
                    evidence_type="OHLCV",
                    artifact_type="NORMALIZED_DATASET",
                    source_identity="fixture-source",
                    coverage_start="2026-01-01",
                    coverage_end="2026-01-01",
                    row_count=1,
                    schema=("date", "close", "volume"),
                    provenance={"vendor": "fixture"},
                    neutral_semantics="Observed price and aggregate volume only.",
                )
            )
            nexus.publish_finding(
                Finding(
                    finding_id="f:1",
                    subject_id="AAPL",
                    statement="Significant result",
                    supporting_result_ids=("r:1",),
                    evidence_ids=("ev:1",),
                    metadata={
                        "significance": "RD promoted",
                        "status": "SUPPORTED",
                        "novel_labels": ["regime-alpha", "path-shape-unknown-to-code"],
                        "nested_science": {"hypothesis_family": "RD_DEFINED"},
                    },
                )
            )
            document = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(document["format"], "MTS_V4_RESEARCH_NEXUS_V1")
            self.assertEqual(
                set(document),
                {"format", "subjects", "evidence_metadata", "findings", "finding_retractions"},
            )
            self.assertEqual(document["finding_retractions"], [])
            serialized = path.read_text(encoding="utf-8")
            self.assertNotIn('"payload"', serialized)
            self.assertNotIn('"rows"', serialized)
            self.assertNotIn('"cache_key"', serialized)

            reopened = JsonResearchNexus(path)
            self.assertEqual(reopened.get_subject("AAPL").ticker, "AAPL")
            self.assertEqual(
                reopened.get_evidence_metadata("ev:1").source_identity,
                "fixture-source",
            )
            finding = reopened.get_finding("f:1")
            self.assertEqual(finding.statement, "Significant result")
            self.assertEqual(finding.metadata["nested_science"]["hypothesis_family"], "RD_DEFINED")

    def test_early_v4_closed_scientific_fields_migrate_into_open_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nexus.json"
            path.write_text(
                json.dumps(
                    {
                        "format": "MTS_V4_RESEARCH_NEXUS_V1",
                        "subjects": [{"subject_id": "AAPL", "ticker": "AAPL", "asset_class": "EQUITY", "attributes": {}}],
                        "evidence_metadata": [],
                        "findings": [
                            {
                                "finding_id": "legacy:f1",
                                "subject_id": "AAPL",
                                "statement": "Legacy early-v4 finding",
                                "significance": "important",
                                "status": "EXPLORATORY",
                                "supporting_result_ids": [],
                                "evidence_ids": [],
                                "applicability": {"regime": "unknown"},
                                "limitations": ["legacy"],
                                "relationships": ["candidate"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            finding = JsonResearchNexus(path).get_finding("legacy:f1")
            self.assertEqual(finding.metadata["significance"], "important")
            self.assertEqual(finding.metadata["status"], "EXPLORATORY")
            self.assertEqual(finding.metadata["applicability"]["regime"], "unknown")


if __name__ == "__main__":
    unittest.main()
