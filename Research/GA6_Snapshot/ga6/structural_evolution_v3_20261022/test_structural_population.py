import random,unittest
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
from ga6.structural_evolution_v3_20261022.structural_population import propose_structural,random_tree
class PopulationTests(unittest.TestCase):
 def test_population_diversity_and_replayable_checkpoint(self):
  rng=random.Random(20261021)
  parents=[(0,StructuralCandidate(initial(n),random_tree(rng)),{}) for n in NICHES]
  pop,report=propose_structural(parents,rng,population=260)
  self.assertEqual(len(pop),260)
  self.assertEqual(report['niches'],13)
  self.assertEqual(len({c.identity() for c in pop}),260)
  for c in pop:self.assertEqual(StructuralCandidate.restore(c.checkpoint()).identity(),c.identity())
  for activity in ('new_structures','sobol_refinement','evolution','challengers'):self.assertGreater(report['counts'].get(activity,0),0)
  self.assertTrue(any(any('op' in child for child in c.entry_tree['children']) for c in pop))
if __name__=='__main__':unittest.main()
