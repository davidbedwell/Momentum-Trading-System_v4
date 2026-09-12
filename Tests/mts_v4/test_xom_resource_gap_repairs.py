from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from Core.deterministic_computation.families import volume_liquidity
from MTS_V4.group_aggregation import group_aggregate
from MTS_V4.standard_methods import (
    compose_aligned_dataset,
    datetime_component,
    descriptive_statistics,
    exact_value_filter,
)


class XomResourceGapRepairTests(unittest.TestCase):
    def test_numeric_provider_strings_are_mechanically_usable(self):
        rows = (
            {"price": "100.5", "dark_pool_volume": "1,250"},
            {"price": "101.5", "dark_pool_volume": "750"},
        )
        stats = descriptive_statistics(
            {"darkpool": rows},
            {"columns": ["price", "dark_pool_volume"]},
        )
        self.assertEqual(stats["columns"]["price"]["count"], 2)
        self.assertEqual(stats["columns"]["dark_pool_volume"]["count"], 2)
        self.assertEqual(stats["columns"]["dark_pool_volume"]["mean"], 1000.0)

    def test_group_aggregate_preserves_exact_category_identity_and_numeric_strings(self):
        rows = (
            {"weekStartDate": "2026-09-01", "summaryTypeCode": "ATS_W_SMBL", "shares": "1,000"},
            {"weekStartDate": "2026-09-01", "summaryTypeCode": "ATS_W_SMBL", "shares": "250"},
            {"weekStartDate": "2026-09-01", "summaryTypeCode": "OTC_W_SMBL", "shares": "500"},
        )
        result = group_aggregate(
            {"finra": rows},
            {
                "group_by": ["weekStartDate", "summaryTypeCode"],
                "aggregations": [
                    {"column": "shares", "statistic": "sum", "output_name": "share_sum"}
                ],
            },
        )
        self.assertEqual(
            result["group_key_values"]["summaryTypeCode"],
            ["ATS_W_SMBL", "OTC_W_SMBL"],
        )
        grouped = result["derived_datasets"]["grouped_dataset"]
        self.assertEqual(grouped[0]["summaryTypeCode"], "ATS_W_SMBL")
        self.assertEqual(grouped[0]["share_sum"], 1250.0)
        self.assertEqual(grouped[1]["summaryTypeCode"], "OTC_W_SMBL")
        self.assertEqual(grouped[1]["share_sum"], 500.0)

    def test_exact_filter_and_datetime_component_preserve_rows_for_rd_authored_aggregation(self):
        source = (
            {"summaryTypeCode": "ATS_W_SMBL", "executed_at": "2026-09-10T14:15:00Z", "volume": "100"},
            {"summaryTypeCode": "OTC_W_SMBL", "executed_at": "2026-09-10T15:45:00Z", "volume": "200"},
        )
        filtered = exact_value_filter(
            {"source": source},
            {"conditions": [{"column": "summaryTypeCode", "value": "ATS_W_SMBL"}]},
        )
        filtered_rows = filtered["derived_datasets"]["filtered_dataset"]
        self.assertEqual(len(filtered_rows), 1)
        self.assertEqual(filtered_rows[0]["volume"], "100")
        self.assertEqual(filtered_rows[0]["__observation_lineage"]["input_row_anchor"], 0)

        transformed = datetime_component(
            {"alerts": source},
            {"column": "executed_at", "output_name": "trade_date", "component": "DATE"},
        )
        rows = transformed["derived_datasets"]["datetime_component"]
        self.assertEqual([row["trade_date"] for row in rows], ["2026-09-10", "2026-09-10"])
        self.assertEqual(transformed["excluded_unparseable"], 0)

    def test_parent_row_position_alignment_uses_only_explicit_lineage_anchor(self):
        parent = (
            {"value": 10},
            {"value": 20},
            {"value": 30},
            {"value": 40},
        )
        child = (
            {
                "event": "a",
                "__observation_lineage": {
                    "input_name": "parent",
                    "input_row_start": 1,
                    "input_row_end": 1,
                    "input_row_anchor": 1,
                    "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
                },
            },
            {
                "event": "b",
                "__observation_lineage": {
                    "input_name": "parent",
                    "input_row_start": 3,
                    "input_row_end": 3,
                    "input_row_anchor": 3,
                    "semantics": "MECHANICAL_INPUT_ROW_LINEAGE_NOT_SCIENTIFIC_INTERPRETATION",
                },
            },
        )
        result = compose_aligned_dataset(
            {"parent": parent, "child": child},
            {
                "alignment": [
                    {"input_name": "parent", "key": {"mode": "ROW_POSITION"}},
                    {"input_name": "child", "key": {"mode": "PARENT_ROW_POSITION"}},
                ],
                "selections": [
                    {"input_name": "parent", "column": "value", "output_name": "value"},
                    {"input_name": "child", "column": "event", "output_name": "event"},
                ],
                "join_type": "INNER",
            },
        )
        rows = result["derived_datasets"]["composed_dataset"]
        self.assertEqual([row["alignment_key"] for row in rows], [1, 3])
        self.assertEqual([row["value"] for row in rows], [20, 40])

    def test_parent_row_position_alignment_fails_closed_without_lineage(self):
        with self.assertRaisesRegex(ValueError, "requires explicit observation lineage"):
            compose_aligned_dataset(
                {"parent": ({"value": 10},), "child": ({"event": "a"},)},
                {
                    "alignment": [
                        {"input_name": "parent", "key": {"mode": "ROW_POSITION"}},
                        {"input_name": "child", "key": {"mode": "PARENT_ROW_POSITION"}},
                    ],
                    "selections": [
                        {"input_name": "parent", "column": "value", "output_name": "value"}
                    ],
                    "join_type": "INNER",
                },
            )

    def test_volume_liquidity_family_exposes_added_liquidity_regime_measurements(self):
        n = 80
        close = pd.Series(np.linspace(90.0, 110.0, n))
        frame = pd.DataFrame(
            {
                "date": pd.date_range("2026-01-01", periods=n, freq="D"),
                "open": close - 0.25,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": np.linspace(1_000_000.0, 2_000_000.0, n),
            }
        )
        measured = volume_liquidity.calculate(frame)
        expected = {
            "absolute_return",
            "intraday_range_pct",
            "amihud_illiquidity_mean_20",
            "amihud_illiquidity_zscore_20",
            "dollar_volume_mean_20",
            "dollar_volume_zscore_20",
            "dollar_volume_cv_20",
            "corwin_schultz_spread_estimate",
        }
        self.assertTrue(expected.issubset(set(measured.columns)))
        self.assertTrue(measured["corwin_schultz_spread_estimate"].dropna().ge(0.0).all())


if __name__ == "__main__":
    unittest.main()
