import unittest
from ga6.structural_independent_v2_20261022.calendar_evidence import build_matrix

class CalendarEvidenceTests(unittest.TestCase):
 def setUp(self):
  self.dates=['2026-01-01','2026-01-02','2026-01-03']
  self.plan={'loss_differential':'candidate_net_return_minus_benchmark_net_return',
             'calendar_start':self.dates[0],'calendar_end':self.dates[-1]}
 def test_aligned_and_deterministic(self):
  a=build_matrix(self.dates,{'b':[.01,.02,0],'a':[0,.03,.01]},[0,.01,0],self.plan)
  b=build_matrix(self.dates,{'a':[0,.03,.01],'b':[.01,.02,0]},[0,.01,0],self.plan)
  self.assertEqual(a['candidate_ids'],['a','b'])
  self.assertEqual(a['evidence_fingerprint'],b['evidence_fingerprint'])
  self.assertEqual(a['differentials'].shape,(3,2))
 def test_missing_day_fails(self):
  with self.assertRaises(ValueError):
   build_matrix(self.dates,{'a':[.01,.02]},[0,0,0],self.plan)
 def test_wrong_dates_fails(self):
  with self.assertRaises(ValueError):
   build_matrix(self.dates,{'a':[.01,.02,0]},[0,0,0],{**self.plan,'calendar_end':'2026-01-04'})
if __name__=='__main__':unittest.main()
