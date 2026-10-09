import unittest,pandas as pd
from Core.layered_ga.gen1_path_release_gate import verify_feature_release
class ReleaseTests(unittest.TestCase):
 def test_known_past(self):
  self.assertEqual(verify_feature_release(pd.DataFrame({'x':[1]}),['2020-01-02T14:30Z'],['2020-01-02T14:00Z'],['x'])['rows'],1)
 def test_future_rejected(self):
  with self.assertRaises(ValueError):verify_feature_release(pd.DataFrame({'x':[1]}),['2020-01-02T14:30Z'],['2020-01-02T15:00Z'],['x'])
 def test_missing_rejected(self):
  with self.assertRaises(ValueError):verify_feature_release(pd.DataFrame({'x':[1]}),['2020-01-02T14:30Z'],[None],['x'])
if __name__=='__main__':unittest.main()
