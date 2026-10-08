import unittest
import pandas as pd
from Core.layered_ga.ga4_fold_isolation import (
    freeze_fold_membership, assert_fold_scoped_frame, forbid_heldout_feedback)


class TestGA4FoldIsolation(unittest.TestCase):
    def setUp(self):
        self.membership = freeze_fold_membership(
            [f"D{i:03}" for i in range(80)],
            [f"H{i:03}" for i in range(37)])

    def test_frozen_membership_and_scope(self):
        frame = pd.DataFrame({"security_id": self.membership["dev80"]})
        scope = self.membership["membership_sha256"] + ":DEV80:recomputed"
        self.assertTrue(assert_fold_scoped_frame(frame, self.membership, "DEV80", predictor_scope=scope))

    def test_reject_all117_cache(self):
        frame = pd.DataFrame({"security_id": self.membership["dev80"] + self.membership["dev37"]})
        scope = self.membership["membership_sha256"] + ":DEV80:recomputed"
        with self.assertRaises(ValueError):
            assert_fold_scoped_frame(frame, self.membership, "DEV80", predictor_scope=scope)

    def test_reject_unproven_recomputation(self):
        frame = pd.DataFrame({"security_id": self.membership["dev80"]})
        with self.assertRaises(ValueError):
            assert_fold_scoped_frame(frame, self.membership, "DEV80", predictor_scope="all117_cache")

    def test_reject_overlap_and_heldout_tuning(self):
        with self.assertRaises(ValueError):
            freeze_fold_membership([f"D{i}" for i in range(80)], ["D0"] + [f"H{i}" for i in range(36)])
        with self.assertRaises(ValueError):
            forbid_heldout_feedback("DEV37", selection_or_tuning=True)
        forbid_heldout_feedback("DEV37", selection_or_tuning=False)


if __name__ == "__main__":
    unittest.main()
