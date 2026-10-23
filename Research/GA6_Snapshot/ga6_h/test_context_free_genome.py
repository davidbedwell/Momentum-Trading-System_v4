import random,unittest
from dataclasses import replace
from context_free_genome import Genome,leaf,random_genome,crossover,mutate,validate_tree

class ContextFreeGenomeTests(unittest.TestCase):
    def test_no_niche_identity(self):
        g=random_genome(random.Random(2))
        self.assertFalse(hasattr(g,'niche'))
        self.assertEqual(g.identity(),replace(g).identity())
    def test_repeated_family_different_windows(self):
        a=leaf(random.Random(1),'momentum');b=dict(a);b['window']=a['window']+1
        self.assertEqual(len(validate_tree({'op':'AND','children':[a,b]})),2)
    def test_duplicate_exact_leaf_rejected(self):
        a=leaf(random.Random(1))
        with self.assertRaises(ValueError):validate_tree({'op':'OR','children':[a,dict(a)]})
    def test_hold_cap(self):
        g=random_genome(random.Random(2))
        with self.assertRaises(ValueError):replace(g,hold_sessions=41).validate()
    def test_global_crossover_deterministic(self):
        a=random_genome(random.Random(4));b=random_genome(random.Random(5))
        c=crossover(a,b,random.Random(6));self.assertTrue(c.validate())
        self.assertEqual(c.identity(),crossover(a,b,random.Random(6)).identity())
    def test_mutation_invariants(self):
        r=random.Random(99);g=random_genome(r)
        for _ in range(500):
            g=mutate(g,r);self.assertTrue(g.validate())
if __name__=='__main__':unittest.main()
