import unittest
from types import SimpleNamespace
from Core.layered_ga.ga4_relationship_catalog import candidate_key, relationship_record


class TestGA4RelationshipCatalog(unittest.TestCase):
    def setUp(self):
        self.curve = SimpleNamespace(
            side="LONG",
            points=tuple({"horizon": h, "ev_net": -0.001 if h < 10 else 0.002,
                          "mae_mean": -0.02, "n": 210, "effective_n": 25}
                         for h in range(1, 64)),
            pareto_horizons=(20, 63),
            pareto_ranges=((20, 20), (63, 63)),
        )

    def test_full_curve_and_negative_evidence_retained(self):
        r = relationship_record(chromosomes=["a", "b"], context={"sector": "technology"},
                                curve=self.curve, fold="DEV80-1", data_provenance="fixture")
        self.assertEqual(len(r["daily_horizon_evidence"]), 63)
        self.assertLess(r["daily_horizon_evidence"][0]["ev_net"], 0)
        self.assertFalse(r["certified"])
        self.assertEqual(r["candidate_id"], candidate_key(["a", "b"], {"sector": "technology"}))

    def test_incomplete_curve_rejected(self):
        self.curve.points = self.curve.points[:-1]
        with self.assertRaises(ValueError):
            relationship_record(chromosomes=["a"], context={"market": "bear"},
                                curve=self.curve, fold="DEV80-1", data_provenance="fixture")

    def test_invalid_combinations_rejected(self):
        for genes in ([], ["a"] * 2, ["a", "b", "c", "d", "e"]):
            with self.assertRaises(ValueError):
                candidate_key(genes, {"market": "normal"})


if __name__ == "__main__":
    unittest.main()
