import unittest
from ga6.structural_independent_v2_20261022.discovery_allocation import allocate,Observation,ACTIVITIES
class AllocationTests(unittest.TestCase):
 def test_initial_400(self):
  self.assertEqual(allocate(),dict(zip(ACTIVITIES,[180,80,100,40])))
 def test_adaptive_capped(self):
  obs={a:Observation(100,0,1000) for a in ACTIVITIES}
  obs['evolution']=Observation(100,100,1)
  r=allocate(obs,generation=5)
  self.assertEqual(sum(r.values()),400)
  self.assertLessEqual(max(r.values()),240)
  self.assertGreaterEqual(min(r.values()),20)
 def test_only_refresh_every_five(self):
  obs={a:Observation(100,100,1) for a in ACTIVITIES}
  self.assertEqual(allocate(obs,generation=6),allocate())
 def test_invalid(self):
  with self.assertRaises(ValueError):allocate(population=2)
if __name__=='__main__':unittest.main()
