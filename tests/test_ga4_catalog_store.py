import tempfile
import unittest

from Core.layered_ga.ga4_catalog_store import append_record, read_records


class TestGA4CatalogStore(unittest.TestCase):
    def record(self):
        return {
            "candidate_id": "abc", "fold": "DEV80-1", "side": "LONG",
            "data_provenance": "fixture",
            "daily_horizon_evidence": [
                {"horizon": h, "ev_net": -0.01, "mae_mean": -0.02}
                for h in range(1, 64)
            ],
        }

    def test_append_and_replay(self):
        with tempfile.TemporaryDirectory() as folder:
            path, created = append_record(folder, self.record())
            self.assertTrue(created)
            self.assertTrue(path.exists())
            again, created = append_record(folder, self.record())
            self.assertEqual(again, path)
            self.assertFalse(created)
            self.assertEqual(len(read_records(folder)), 1)

    def test_conflicting_replay_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            append_record(folder, self.record())
            changed = self.record()
            changed["daily_horizon_evidence"][0]["ev_net"] = 0.5
            with self.assertRaises(ValueError):
                append_record(folder, changed)

    def test_missing_horizon_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            bad = self.record()
            bad["daily_horizon_evidence"].pop()
            with self.assertRaises(ValueError):
                append_record(folder, bad)


if __name__ == "__main__":
    unittest.main()
