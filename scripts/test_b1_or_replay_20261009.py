import unittest
from Core.layered_ga.defensive_daily_replay import DayRecord,replay
from Core.layered_ga.b1_slow_bear import B1SlowBear
class TestB1(unittest.TestCase):
 def test_or_independence_and_r1(self):
  v=replay([DayRecord('2026-01-01',False,False,False,False,True),DayRecord('2026-01-02',False,False,False,True,False)])
  self.assertTrue(v[0]['crash_entry']);self.assertTrue(v[1]['r1_exit'])
 def test_b1_internal_and(self):
  d=B1SlowBear();
  for _ in range(200):self.assertFalse(d.update(spy_close=100,lagged_funding_percentile=.9))
  for _ in range(9):self.assertFalse(d.update(spy_close=80,lagged_funding_percentile=.9))
  self.assertFalse(d.update(spy_close=80,lagged_funding_percentile=.6))
  self.assertTrue(d.update(spy_close=80,lagged_funding_percentile=.9))
 def test_no_missing_funding_approval(self):
  d=B1SlowBear()
  for _ in range(220):self.assertFalse(d.update(spy_close=100 if len(d.closes)<200 else 70,lagged_funding_percentile=None))
if __name__=='__main__':unittest.main()
