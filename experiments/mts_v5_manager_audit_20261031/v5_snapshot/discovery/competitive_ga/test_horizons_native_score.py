import unittest
from .horizons_native_score import score,FEATURES
class TestScore(unittest.TestCase):
 def test_original_sparse_dot_product(self):
  self.assertAlmostEqual(score({'ids':[0,8,27],'w':[2,-1,3]},{FEATURES[0]:.5,FEATURES[8]:.2,FEATURES[27]:.4}),2.)
 def test_missing_feature_fails_closed(self):
  with self.assertRaises(ValueError):score({'ids':[0],'w':[1]}, {})
 def test_bad_id_fails_closed(self):
  with self.assertRaises(ValueError):score({'ids':[28],'w':[1]}, {})
if __name__=='__main__':unittest.main()
