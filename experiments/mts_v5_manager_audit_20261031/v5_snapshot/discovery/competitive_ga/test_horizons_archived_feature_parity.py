import unittest
import pandas as pd
from .horizons_native_score import FEATURES
from .horizons_archived_feature_parity import compare
class TestArchivedFeatureParity(unittest.TestCase):
 def test_array_formula(self):
  rows=[]
  for i,d in enumerate(pd.bdate_range('2026-01-01',periods=90)):
   for j,t in enumerate(('A','B','C','D')):
    row={'date':d,'ticker':t}
    row.update({name:(i+j*j+1)/100 for name in FEATURES});rows.append(row)
  r=compare(pd.DataFrame(rows))
  self.assertEqual(r['nonmatching_gt_1e_6'],0)
if __name__=='__main__':unittest.main()
