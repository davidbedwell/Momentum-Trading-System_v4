import tempfile,unittest
from pathlib import Path
from ga6.structural_evolution_v3_20261022.statistical_preregistration import register,verify
class PreregistrationTests(unittest.TestCase):
 def test_immutable(self):
  p={'benchmark':'cash','loss_differential':'net calendar daily','candidate_family_hash':'abc',
     'data_fingerprint':'def','calendar_start':'2020-01-01','calendar_end':'2021-01-01',
     'block_length':20,'replications':999,'seed':10,'alpha':.05,
     'method':'synchronized_max_t_screen','selection_rule':'global','family_trial_count':100}
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'plan.json'
   digest=register(path,p)
   self.assertEqual(verify(path,digest),p)
   self.assertEqual(register(path,p),digest)
   with self.assertRaises(PermissionError):register(path,{**p,'benchmark':'SPY'})
   with self.assertRaises(ValueError):register(Path(d)/'bad.json',{**p,'family_trial_count':0})
if __name__=='__main__':unittest.main()
