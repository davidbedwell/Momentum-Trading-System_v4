import tempfile,unittest
from pathlib import Path
from ga6.structural_evolution_v3_20261022.validation_governance import InformationHorizon,assess_splits,LockedAccess
class GovernanceTests(unittest.TestCase):
 def test_insufficient_duration(self):
  dates=[f'2025-{m:02d}-{d:02d}' for m in range(1,5) for d in range(1,21)]
  result=assess_splits(dates,{},InformationHorizon(40,160,12))
  self.assertFalse(result['feasible']);self.assertEqual(result['horizon_sessions'],160)
 def test_one_use_and_retirement(self):
  with tempfile.TemporaryDirectory() as temp:
   gate=LockedAccess(Path(temp)/'gate.sqlite')
   plan={'benchmark':'cash','loss_definition':'daily net differential','pass_criteria':'predeclared alpha','failure_policy':'retire','calendar_start':'2024-01-01','calendar_end':'2025-01-01','information_horizon_sessions':160,'data_fingerprint':'abc','permitted_consultations':1}
   digest=gate.register('locked_validation','abc',plan)
   gate.consume('locked_validation','abc',digest)
   with self.assertRaises(PermissionError):gate.consume('locked_validation','abc',digest)
   gate.retire('locked_validation')
   with self.assertRaises(Exception):gate.register('locked_validation','abc',plan)
   gate.close()
if __name__=='__main__':unittest.main()
