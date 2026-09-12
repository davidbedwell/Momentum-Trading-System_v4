from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from MTS_V4.validation_frontier import (
    BlindEvidenceWindow,
    JsonValidationFrontierStore,
    SubjectValidationFrontier,
    ValidationFrontierError,
    trial_id,
)


class ValidationFrontierTests(unittest.TestCase):
    def test_trials_replicate_one_hypothesis_identity(self):
        self.assertEqual("AMD-H001-T01", trial_id("AMD-H001", 1))
        self.assertEqual("AMD-H001-T20", trial_id("AMD-H001", 20))

    def test_window_moves_sealed_to_locked_to_exposed_without_changing_dates(self):
        window = BlindEvidenceWindow(
            window_id="AMD-W01",
            subject_id="equity:AMD",
            start_date="2026-01-02",
            end_date="2026-03-31",
        )
        locked = window.lock(
            hypothesis_id="AMD-H001",
            trial_ids=tuple(trial_id("AMD-H001", index) for index in range(1, 21)),
        )
        exposed = locked.expose()

        self.assertEqual("LOCKED_FOR_VALIDATION", locked.state)
        self.assertEqual("AMD-H001", locked.hypothesis_id)
        self.assertEqual(20, len(locked.trial_ids))
        self.assertEqual("EXPOSED", exposed.state)
        self.assertEqual(window.start_date, exposed.start_date)
        self.assertEqual(window.end_date, exposed.end_date)
        self.assertIsNotNone(exposed.exposed_at)

    def test_frontier_rejects_overlapping_blind_windows(self):
        frontier = SubjectValidationFrontier(subject_id="equity:AMD")
        frontier = frontier.seal_window(
            BlindEvidenceWindow(
                window_id="AMD-W01",
                subject_id="equity:AMD",
                start_date="2026-01-01",
                end_date="2026-02-01",
            )
        )
        with self.assertRaisesRegex(ValidationFrontierError, "may not overlap"):
            frontier.seal_window(
                BlindEvidenceWindow(
                    window_id="AMD-W02",
                    subject_id="equity:AMD",
                    start_date="2026-01-15",
                    end_date="2026-03-01",
                )
            )

    def test_exposed_window_remains_durable_and_cannot_be_relocked(self):
        window = BlindEvidenceWindow(
            window_id="AMD-W01",
            subject_id="equity:AMD",
            start_date="2026-01-02",
            end_date="2026-03-31",
        ).lock(
            hypothesis_id="AMD-H001",
            trial_ids=("AMD-H001-T01",),
        ).expose()
        with self.assertRaisesRegex(ValidationFrontierError, "only SEALED"):
            window.lock(hypothesis_id="AMD-H001", trial_ids=("AMD-H001-T02",))

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "frontier.json"
            store = JsonValidationFrontierStore(path)
            frontier = SubjectValidationFrontier(subject_id="equity:AMD").seal_window(
                BlindEvidenceWindow(
                    window_id="AMD-W01",
                    subject_id="equity:AMD",
                    start_date="2026-01-02",
                    end_date="2026-03-31",
                )
            )
            frontier = frontier.update_window(
                frontier.windows[0].lock(
                    hypothesis_id="AMD-H001",
                    trial_ids=("AMD-H001-T01",),
                )
            )
            frontier = frontier.update_window(frontier.windows[0].expose())
            store.save(frontier)
            loaded = store.load(subject_id="equity:AMD")
            self.assertEqual("EXPOSED", loaded.windows[0].state)


if __name__ == "__main__":
    unittest.main()
