from __future__ import annotations

import unittest

from MTS_V4.participation_analysis import METHOD_ID, analysis_method, method_spec


class ParticipationContextTests(unittest.TestCase):
    def test_contract_keeps_threshold_and_catalyst_science_with_rd(self):
        spec = method_spec()
        self.assertEqual(spec.method_id, METHOD_ID)
        self.assertFalse(spec.metadata["hard_coded_float_threshold"])
        self.assertFalse(spec.metadata["hard_coded_relative_volume_threshold"])
        self.assertEqual(spec.metadata["threshold_selection"], "AI_RESEARCH_DIRECTOR_ONLY")
        self.assertEqual(spec.metadata["catalyst_classification"], "AI_RESEARCH_DIRECTOR_ONLY")
        self.assertEqual(spec.metadata["interaction_definition"], "AI_RESEARCH_DIRECTOR_ONLY")
        self.assertEqual(
            {parameter.name for parameter in spec.parameters},
            {"adv_window", "event_window_days"},
        )

    def test_measurement_exposes_continuous_values_without_threshold_labels(self):
        method = analysis_method()
        ohlcv = [
            {"date": "2026-09-10", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 100},
            {"date": "2026-09-11", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 200},
            {"date": "2026-09-12", "open": 10, "high": 12, "low": 9, "close": 11, "volume": 900},
        ]
        structure = [{"as_of_utc": "2026-09-12T22:00:00+00:00", "float_shares": 1_000}]
        events = [
            {
                "event_time": "2026-09-12T12:00:00+00:00",
                "event_date": "2026-09-12",
                "event_type": "NEWS",
                "headline": "Company announces material contract",
                "publisher": "Example",
            }
        ]
        output = method.implementation(
            {"ohlcv": ohlcv, "structure": structure, "events": events},
            {"adv_window": 2, "event_window_days": 0},
        )

        latest = output["latest_session"]
        self.assertAlmostEqual(latest["relative_volume"], 6.0)
        self.assertAlmostEqual(output["current_float_turnover"], 0.9)
        self.assertEqual(latest["proximate_event_count"], 1)
        self.assertEqual(latest["proximate_event_records"][0]["headline"], "Company announces material contract")
        self.assertNotIn("low_float", latest)
        self.assertNotIn("high_rvol", latest)
        self.assertNotIn("real_catalyst", latest)
        self.assertEqual(
            output["scientific_authority"]["human_low_float_high_rvol_catalyst_idea"],
            "NONBINDING_RESEARCH_LEAD_ONLY",
        )

    def test_current_float_is_not_back_projected_into_historical_rows(self):
        method = analysis_method()
        output = method.implementation(
            {
                "ohlcv": [
                    {"date": "2026-09-10", "close": 10, "volume": 100},
                    {"date": "2026-09-11", "close": 10, "volume": 200},
                ],
                "structure": [{"float_shares": 5_000_000}],
            },
            {"adv_window": 2, "event_window_days": 0},
        )
        rows = output["derived_datasets"]["participation_event_panel"]
        self.assertTrue(all("float_shares" not in row for row in rows))
        self.assertTrue(all("float_turnover" not in row for row in rows))
        self.assertIn("not applied to historical dates", output["historical_float_limitation"])


if __name__ == "__main__":
    unittest.main()
