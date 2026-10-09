import unittest
import numpy as np,pandas as pd
from Core.layered_ga.gen1_path_study_split import split_mask,validate_assignment
class SplitTests(unittest.TestCase):
 def test_purge(self):
  cal=pd.bdate_range('2020-01-01',periods=200)
  m=split_mask(cal,cal,end=str(cal[100].date()),purge=63)
  self.assertTrue(m[36]);self.assertFalse(m[37]);self.assertFalse(m[100])
 def test_missing_calendar(self):
  cal=pd.bdate_range('2020-01-01',periods=100)
  with self.assertRaises(ValueError):split_mask([pd.Timestamp('2020-01-04')],cal)
 def test_assignment(self):
  x={'horizon':10,'checkpoints':[1,2,3,5,7],'status':'TRAIN_ONLY_HORIZON_PROVISIONAL_UNCERTIFIED'}
  self.assertEqual(len(validate_assignment(x)),5)
  x['checkpoints']=[5]
  with self.assertRaises(ValueError):validate_assignment(x)
if __name__=='__main__':unittest.main()
