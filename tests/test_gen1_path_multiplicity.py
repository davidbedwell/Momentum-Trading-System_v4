import unittest,numpy as np
from Core.layered_ga.gen1_path_multiplicity import holm_adjust,benjamini_hochberg
class MultiplicityTests(unittest.TestCase):
 def test_holm(self):
  np.testing.assert_allclose(holm_adjust([.03,.01,.04]),[.06,.03,.06])
 def test_bh(self):
  np.testing.assert_allclose(benjamini_hochberg([.03,.01,.04]),[.04,.03,.04])
 def test_invalid(self):
  with self.assertRaises(ValueError):holm_adjust([-.1])
  with self.assertRaises(ValueError):benjamini_hochberg([np.nan])
 def test_empty(self):
  self.assertEqual(len(holm_adjust([])),0)
if __name__=='__main__':unittest.main()
