from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from MTS_V4.contracts import SubjectMetadata
from MTS_V4.sources import CsvFileSource, TabularSourceSpec
from MTS_V4.standard_methods import (
    classification_metrics,
    rolling_statistics,
    standard_method_catalog,
    threshold_event_indices,
)


class SourcesAndAnalysisExpansionTests(unittest.TestCase):
    def test_csv_source_records_reacquisition_metadata_without_interpretation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aapl.csv"
            path.write_text("date,close,volume\n2026-01-01,100,10\n2026-01-02,101,12\n", encoding="utf-8")
            source = CsvFileSource(path, TabularSourceSpec(
                evidence_type="OHLCV",
                artifact_type="NORMALIZED_DATASET",
                neutral_semantics="Observed rows; no scientific meaning inferred by Intake.",
                source_identity="fixture",
                time_column="date",
            ))
            payload = tuple(source.acquire(SubjectMetadata(subject_id="AAPL", ticker="AAPL")))[0]
            self.assertEqual(payload.row_count, 2)
            self.assertEqual(payload.coverage_start, "2026-01-01")
            self.assertEqual(payload.coverage_end, "2026-01-02")
            self.assertIn("sha256", payload.provenance)
            self.assertIn("acquired_at_utc", payload.provenance)
            self.assertNotIn("relevance", payload.provenance)

    def test_expanded_catalog_requires_rd_authored_scientific_parameters(self):
        catalog = standard_method_catalog()
        expected = {
            "analysis.rolling.statistics": {"column", "window", "statistic"},
            "analysis.events.threshold": {"column", "operator", "threshold"},
            "analysis.performance.binary_classification": {"predicted_column", "actual_column", "positive_value"},
        }
        for method_id, names in expected.items():
            spec = catalog.get(method_id)
            self.assertEqual({item.name for item in spec.parameters}, names)
            self.assertTrue(all(item.required for item in spec.parameters))

    def test_rolling_and_threshold_are_exact_measurements(self):
        evidence = {"e": [{"x": 1.0}, {"x": 3.0}, {"x": 5.0}]}
        rolling = rolling_statistics(evidence, {"column": "x", "window": 2, "statistic": "mean"})
        self.assertEqual([item["value"] for item in rolling["observations"]], [2.0, 4.0])
        events = threshold_event_indices(evidence, {"column": "x", "operator": "GT", "threshold": 2.0})
        self.assertEqual([item["index"] for item in events["events"]], [1, 2])

    def test_classification_metrics_measure_rd_supplied_labels(self):
        result = classification_metrics(
            {"e": [{"p":"UP","a":"UP"},{"p":"UP","a":"DOWN"},{"p":"DOWN","a":"UP"},{"p":"DOWN","a":"DOWN"}]},
            {"predicted_column":"p","actual_column":"a","positive_value":"UP"},
        )
        self.assertEqual(result["true_positive"], 1)
        self.assertEqual(result["false_positive"], 1)
        self.assertEqual(result["false_negative"], 1)
        self.assertEqual(result["true_negative"], 1)
        self.assertEqual(result["accuracy"], 0.5)


if __name__ == "__main__":
    unittest.main()
