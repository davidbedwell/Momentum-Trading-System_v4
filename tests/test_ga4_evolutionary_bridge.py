import tempfile
import unittest
from unittest.mock import patch

from Core.layered_ga.ga4_evolutionary_bridge import run_family_discovery
from Core.layered_ga.ga4_catalog_store import read_records


class TestGA4EvolutionaryBridge(unittest.TestCase):
    def test_persists_all_proposals_before_selection(self):
        with tempfile.TemporaryDirectory() as folder:
            seen = []

            def fake_evaluate(**kwargs):
                genome = kwargs["chromosomes"][0][1]
                value = genome["x"]
                return {
                    "candidate_id": f"candidate-{value}", "fold": "DEV80",
                    "side": "LONG", "data_provenance": "fixture",
                    "daily_horizon_evidence": [
                        {"horizon": h, "ev_net": -value, "lcb95": -value,
                         "mae_mean": -0.1, "mae_tail5": -0.2,
                         "n": 1, "effective_n": 1}
                        for h in range(1, 64)],
                    "pareto_horizons": [], "pareto_ranges": [],
                    "certified": False,
                }

            def fake_evolve(space, evaluate, **kwargs):
                evaluate({"x": 1})
                evaluate({"x": 2})
                seen.extend(read_records(folder))
                return {"generations": [], "unique_evaluations": 2}

            with patch("Core.layered_ga.ga4_evolutionary_bridge.evaluate_conditional_candidate", side_effect=fake_evaluate), patch("Core.layered_ga.ga4_evolutionary_bridge.evolve", side_effect=fake_evolve):
                result = run_family_discovery(
                    space=None, family="MOMENTUM", compiler=None,
                    context_mask=None, context={"market": "fixture"},
                    paths=None, costs=None, cluster_ids=None, fold="DEV80",
                    data_provenance="fixture", catalog_dir=folder, seed=1)
            self.assertEqual(len(seen), 2)
            self.assertEqual({r["candidate_id"] for r in seen}, {"candidate-1", "candidate-2"})
            self.assertEqual(len(result["saved"]), 2)
            self.assertFalse(result["certified"])


if __name__ == "__main__":
    unittest.main()
