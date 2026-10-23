import tempfile,unittest
from pathlib import Path
from ga6.structural_evolution_v3_20261022.development_feedback_ledger import DevelopmentLedger
from ga6.structural_evolution_v3_20261022.discovery_allocation import allocate
class LedgerTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.l=DevelopmentLedger(Path(self.tmp.name)/'ledger.sqlite')
 def tearDown(self):self.l.close();self.tmp.cleanup()
 def test_single_credit_and_lag(self):
  self.l.record_trial('t1','g1','evolution','NICHE-0001',2,'development_feedback','same_regime',3)
  self.assertFalse(self.l.observations(3))
  self.l.record_trial('t1b','g1b','challengers','NICHE-0001',2,'development_feedback','same_regime',3)
  self.l.credit('t1',1,'evidence-hash')
  self.l.credit('t1b',0,'evidence-hash-b')
  self.assertFalse(self.l.observations(3))
  self.assertEqual(self.l.observations(4)['evolution'].novel,1)
  with self.assertRaises(ValueError):self.l.credit('t1',1,'evidence-hash')
 def test_discovery_never_credited(self):
  self.l.record_trial('t2','g2','new_structures','NICHE-0001',1,'discovery','normal',2)
  with self.assertRaises(ValueError):self.l.credit('t2',1,'hash')
 def test_append_only_ids(self):
  args=('t3','g3','challengers','NICHE-0002',1,'development_feedback','normal',1)
  self.l.record_trial(*args)
  with self.assertRaises(Exception):self.l.record_trial(*args)
 def test_decision_immutable(self):
  weights=allocate();self.l.record_decision(5,weights,3)
  with self.assertRaises(Exception):self.l.record_decision(5,weights,3)
if __name__=='__main__':unittest.main()
