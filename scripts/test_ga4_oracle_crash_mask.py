import unittest
import pandas as pd
from Core.layered_ga.ga4_oracle_crash_mask import admissible_decisions,frozen_episode_intervals
class MaskTests(unittest.TestCase):
 def test_entry_and_crossing(self):
  c=pd.bdate_range('2020-01-01',periods=35)
  ep={'test':{'peak':str(c[5].date()),'trough':str(c[15].date())}}
  start,end=frozen_episode_intervals(c,ep,offset=2)[0]
  self.assertEqual(start,c[7]);self.assertEqual(end,c[17])
  a=admissible_decisions(c,c,ep,[1,5],offset=2)
  self.assertTrue(a[0,0]);self.assertFalse(a[5,5//5]);self.assertFalse(a[6,0]);self.assertTrue(a[17,0]);self.assertTrue(a[18,0])
 def test_missing_episode_fails_closed(self):
  c=pd.bdate_range('2020-01-01',periods=35)
  with self.assertRaises(ValueError):frozen_episode_intervals(c,{'x':{'peak':'1999-01-01','trough':'2020-01-20'}})
if __name__=='__main__':unittest.main()
