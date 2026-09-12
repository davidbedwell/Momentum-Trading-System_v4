from __future__ import annotations

import unittest

from MTS_V4.intake import IntakePayload
from MTS_V4.temporal_sequestration import (
    TemporalSequestrationError,
    TemporalSequestrationPlan,
    sequester_temporal_payload,
)


class TemporalSequestrationTests(unittest.TestCase):
    @staticmethod
    def _source() -> IntakePayload:
        rows = [
            {"date": "2026-01-02", "close": 10.0},
            {"date": "2026-01-05", "close": 11.0},
            {"date": "2026-01-06", "close": 12.0},
            {"date": "2026-01-07", "close": 13.0},
            {"date": "2026-01-08", "close": 14.0},
        ]
        return IntakePayload(
            payload=rows,
            evidence_type="OHLCV",
            artifact_type="NORMALIZED_DATASET",
            source_identity="TEST",
            coverage_start="2026-01-02",
            coverage_end="2026-01-08",
            row_count=len(rows),
            schema=("date", "close"),
            provenance={"provider": "test"},
            neutral_semantics="test rows",
        )

    def test_split_keeps_blind_and_post_blind_rows_out_of_exploration(self):
        result = sequester_temporal_payload(
            self._source(),
            plan=TemporalSequestrationPlan(
                temporal_field="date",
                exploration_end_date="2026-01-05",
                blind_start_date="2026-01-06",
                blind_end_date="2026-01-07",
            ),
        )
        self.assertEqual(2, result.exploration.row_count)
        self.assertEqual(2, result.blind.row_count)
        self.assertEqual(1, result.excluded_after_blind.row_count)
        self.assertEqual("EXPLORATION_VISIBLE", result.exploration.provenance["temporal_partition"])
        self.assertEqual("BLIND_SEALED", result.blind.provenance["temporal_partition"])
        self.assertEqual(
            "POST_BLIND_UNEXPOSED",
            result.excluded_after_blind.provenance["temporal_partition"],
        )
        self.assertEqual(
            result.exploration.provenance["parent_source_content_identity"],
            result.blind.provenance["parent_source_content_identity"],
        )

    def test_plan_does_not_choose_scientific_boundary(self):
        with self.assertRaisesRegex(TemporalSequestrationError, "blind_start_date"):
            TemporalSequestrationPlan(
                temporal_field="date",
                exploration_end_date="2026-01-06",
                blind_start_date="2026-01-06",
                blind_end_date="2026-01-07",
            )

    def test_unassigned_source_rows_are_rejected_not_silently_dropped(self):
        with self.assertRaisesRegex(TemporalSequestrationError, "unassigned temporal gap"):
            sequester_temporal_payload(
                self._source(),
                plan=TemporalSequestrationPlan(
                    temporal_field="date",
                    exploration_end_date="2026-01-02",
                    blind_start_date="2026-01-06",
                    blind_end_date="2026-01-07",
                ),
            )


if __name__ == "__main__":
    unittest.main()
