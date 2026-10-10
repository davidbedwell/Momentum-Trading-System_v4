import unittest
from Core.layered_ga.defensive_daily_replay import DayRecord,replay
D=lambda d,a=False,b=False,c=False,r1=False:DayRecord(d,a,b,c,r1)
class ReplayTests(unittest.TestCase):
 def test_abc_each_triggers(self):
  for name in ('a','b','c'):
   row=D('2026-01-01',**{name:True});r=replay([row])[0]
   self.assertEqual(r['state'],'DEFENSIVE');self.assertEqual(len(r['cash_first_actions']),2)
 def test_no_r1_no_exit(self):
  rows=[D('2026-01-01',a=True)]+[D('2026-01-%02d'%i) for i in range(2,31)]
  self.assertTrue(all(x['state']=='DEFENSIVE' for x in replay(rows)))
 def test_r1_only_ends_and_new_crash_reenters(self):
  out=replay([D('2026-01-01',b=True),D('2026-01-02'),D('2026-01-03',r1=True),D('2026-01-04',c=True)])
  self.assertEqual([x['state'] for x in out],['DEFENSIVE','DEFENSIVE','NORMAL','DEFENSIVE'])
  self.assertEqual(sum(x['crash_entry'] for x in out),2)
 def test_simultaneous_abc_r1(self):
  self.assertEqual(replay([D('2026-01-01',a=True,r1=True)])[0]['state'],'DEFENSIVE')
 def test_missing_fail_closed(self):
  with self.assertRaises(ValueError):replay([D('2026-01-01',a=None)])
 def test_duplicate_dates_rejected(self):
  with self.assertRaises(ValueError):replay([D('2026-01-01'),D('2026-01-01')])
 def test_unsorted_rejected(self):
  with self.assertRaises(ValueError):replay([D('2026-01-02'),D('2026-01-01')])
if __name__=='__main__':unittest.main()
