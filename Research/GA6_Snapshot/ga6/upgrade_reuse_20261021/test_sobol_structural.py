import random,unittest
from ga6.upgrade_reuse_20261021.structural_population import random_tree,leaves
class SobolStructuralTests(unittest.TestCase):
 def test_deterministic_indexed_sobol(self):
  parent=random_tree(random.Random(10))
  a=random_tree(random.Random(1),'sobol_refinement',parent,sobol_index=4)
  b=random_tree(random.Random(99),'sobol_refinement',parent,sobol_index=4)
  c=random_tree(random.Random(1),'sobol_refinement',parent,sobol_index=5)
  self.assertEqual(a,b)
  self.assertNotEqual(a,c)
  self.assertEqual([x['family'] for x in leaves(parent)],[x['family'] for x in leaves(a)])
  self.assertTrue(all(-1<=x['threshold']<=1 for x in leaves(a)))
if __name__=='__main__':unittest.main()
