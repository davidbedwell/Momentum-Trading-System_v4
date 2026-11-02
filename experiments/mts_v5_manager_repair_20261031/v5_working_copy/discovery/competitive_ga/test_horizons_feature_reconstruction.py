import unittest
import pandas as pd
from .horizons_feature_reconstruction import raw_panel,STOCK_SOURCE
class TestFeatures(unittest.TestCase):
 def setUp(self):
  self.frame=pd.DataFrame([dict(date=pd.Timestamp('2026-01-01'),ticker='A',eligible=True,**{v:0.2 for v in STOCK_SOURCE.values()},**{'breadth_above_sma_200__v1':.5,'breadth_positive_20__v1':.6})])
 def test_external_required(self):
  with self.assertRaisesRegex(ValueError,'external stress'):raw_panel(self.frame)
 def test_missing_column(self):
  with self.assertRaisesRegex(ValueError,'missing original'):raw_panel(self.frame.drop(columns=['return_5__v1']))
if __name__=='__main__':unittest.main()
