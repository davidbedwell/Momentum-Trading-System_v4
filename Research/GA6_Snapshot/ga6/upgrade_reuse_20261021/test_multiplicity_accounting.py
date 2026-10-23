import tempfile,unittest
from pathlib import Path
from ga6.upgrade_reuse_20261021.development_feedback_ledger import DevelopmentLedger
from ga6.upgrade_reuse_20261021.multiplicity_accounting import family_census,require_complete_family
class LedgerCensusTests(unittest.TestCase):
 def test_feedback_is_in_family(self):
  with tempfile.TemporaryDirectory() as d:
   l=DevelopmentLedger(Path(d)/'x.sqlite')
   l.record_trial('d','c','evolution','n',0,'discovery','b',1)
   l.record_trial('f','c','evolution','n',1,'development_feedback','b',1)
   l.credit('f',1,'evidence')
   c=family_census(l,1,1)
   self.assertEqual(require_complete_family(c),2)
   self.assertEqual(c['credited_feedback_trials'],1)
   with self.assertRaises(ValueError):family_census(l,1,0)
   with self.assertRaises(PermissionError):require_complete_family(family_census(l))
   l.close()
if __name__=='__main__':unittest.main()
