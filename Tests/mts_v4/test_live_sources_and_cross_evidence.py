from __future__ import annotations

import unittest

from MTS_V4.cross_evidence import METHOD_ID, cross_evidence_analysis_method, cross_evidence_method_spec
from MTS_V4.live_sources import FinraWeeklyOffExchangeSource, UnusualWhalesDarkPoolSource, UnusualWhalesFlowAlertsSource


class LiveSourcesAndCrossEvidenceTests(unittest.TestCase):
    def test_live_sources_accept_external_credentials_without_embedding_values(self):
        dark = UnusualWhalesDarkPoolSource(api_key="dummy")
        options = UnusualWhalesFlowAlertsSource(api_key="dummy")
        finra = FinraWeeklyOffExchangeSource(client_id="dummy-id", client_secret="dummy-secret")
        self.assertEqual(dark.api_key, "dummy")
        self.assertEqual(options.api_key, "dummy")
        self.assertEqual(finra.client_id, "dummy-id")
        self.assertEqual(finra.client_secret, "dummy-secret")

    def test_cross_evidence_contract_exposes_every_scientific_alignment_choice(self):
        spec = cross_evidence_method_spec()
        self.assertEqual(spec.method_id, METHOD_ID)
        names = {parameter.name for parameter in spec.parameters}
        self.assertEqual(
            names,
            {
                "left_evidence_id", "right_evidence_id", "left_time_column", "right_time_column",
                "left_value_column", "right_value_column", "period", "left_aggregation",
                "right_aggregation", "correlation_type",
            },
        )
        self.assertTrue(spec.exploration_allowed)
        self.assertTrue(spec.validation_allowed)
        self.assertTrue(spec.metadata["cross_evidence"])

    def test_cross_evidence_temporal_correlation_is_mechanical(self):
        method = cross_evidence_analysis_method()
        left = [
            {"date": "2026-01-01", "volume": 100},
            {"date": "2026-01-02", "volume": 200},
            {"date": "2026-01-03", "volume": 300},
        ]
        right = [
            {"executed_at": "2026-01-01T12:00:00Z", "premium": 10},
            {"executed_at": "2026-01-02T12:00:00Z", "premium": 20},
            {"executed_at": "2026-01-03T12:00:00Z", "premium": 30},
        ]
        output = method.implementation(
            {"evidence:ohlcv": left, "evidence:dark": right},
            {
                "left_evidence_id": "evidence:ohlcv",
                "right_evidence_id": "evidence:dark",
                "left_time_column": "date",
                "right_time_column": "executed_at",
                "left_value_column": "volume",
                "right_value_column": "premium",
                "period": "day",
                "left_aggregation": "sum",
                "right_aggregation": "sum",
                "correlation_type": "pearson",
            },
        )
        self.assertEqual(output["paired_period_count"], 3)
        self.assertAlmostEqual(output["correlation"], 1.0)
        self.assertEqual(output["interpretation_boundary"], "TEMPORAL_ALIGNMENT_AND_ASSOCIATION_ONLY_NOT_CAUSATION")


if __name__ == "__main__":
    unittest.main()
