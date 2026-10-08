import unittest
import numpy as np
from Core.layered_ga.ga4_heldout_validation import validate_frozen_selection,digest_selection

class HeldoutTests(unittest.TestCase):
    def test_frozen_selection_deterministic(self):
        self.assertEqual(digest_selection([{"x":1}]),digest_selection([{"x":1}]))
    def test_misalignment_fails(self):
        with self.assertRaises(ValueError):
            validate_frozen_selection([True],[True,False],[.1],[1],selection_digest="frozen")
    def test_insufficient_independent_clusters_fails_closed(self):
        r=validate_frozen_selection([True]*4,[True]*4,[.1]*4,[1,1,2,2],selection_digest="frozen")
        self.assertFalse(r["heldout_pass"])
        self.assertFalse(r["independently_verified"])
    def test_selection_adjustment_not_falsely_certified(self):
        r=validate_frozen_selection([True]*30,[True]*30,[.1]*30,list(range(30)),selection_digest="frozen")
        self.assertFalse(r["independently_verified"])
if __name__=="__main__":
    unittest.main()
