"""Regression tests for GA4 complete daily forward horizons."""
import unittest
from Core.layered_ga.ga4_horizon_contract import FORWARD_HORIZONS, validate_horizons


class TestGA4HorizonContract(unittest.TestCase):
    def test_all_daily_horizons(self):
        self.assertEqual(len(FORWARD_HORIZONS), 63)
        self.assertEqual(FORWARD_HORIZONS, tuple(range(1, 64)))
        self.assertEqual(validate_horizons(FORWARD_HORIZONS), FORWARD_HORIZONS)

    def test_reject_legacy_sampled_horizons(self):
        with self.assertRaises(ValueError):
            validate_horizons((1, 3, 5, 10, 15, 20, 63))

    def test_reject_missing_or_duplicate_horizon(self):
        with self.assertRaises(ValueError):
            validate_horizons(tuple(range(1, 63)))
        with self.assertRaises(ValueError):
            validate_horizons((*range(1, 64), 63))


if __name__ == "__main__":
    unittest.main()
