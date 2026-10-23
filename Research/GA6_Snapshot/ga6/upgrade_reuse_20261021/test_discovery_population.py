import unittest,random
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga6.upgrade_reuse_20261021.discovery_population import sobol_variant,propose
class DiscoveryTests(unittest.TestCase):
 def test_sobol_valid_deterministic(self):
  g=initial(NICHES[0]);self.assertEqual(sobol_variant(g,17,3),sobol_variant(g,17,3));self.assertTrue(sobol_variant(g,17,3).valid())
 def test_all_tracks_and_niches(self):
  scored=[(0.,initial(n),{}) for n in NICHES]
  members,info=propose(scored,random.Random(5),400)
  self.assertEqual(len(members),400);self.assertEqual(len({g.identity() for g in members}),400)
  self.assertEqual(info['niches'],13)
  for activity in ('new_structures','sobol_refinement','evolution','challengers'):self.assertGreater(info['actual'].get(activity,0),0)
if __name__=='__main__':unittest.main()
