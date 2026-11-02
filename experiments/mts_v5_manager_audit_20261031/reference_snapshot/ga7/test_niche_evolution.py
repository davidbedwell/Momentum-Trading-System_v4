import unittest
from ga7.engine import niche_population_groups, breed_by_group
class NicheEvolutionTests(unittest.TestCase):
 def test_groups(self):
  groups=niche_population_groups([f'niche-{i:04d}' for i in range(1,14)])
  self.assertEqual(len(groups),14)
  self.assertIn('NON_NICHE',groups)
if __name__=='__main__':unittest.main()
