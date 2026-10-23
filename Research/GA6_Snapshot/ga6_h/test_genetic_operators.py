import random,unittest
from dataclasses import replace
from context_free_genome import Genome,leaf,random_genome
from genetic_operators import tree_crossover,structural_mutation
from context_scoring import score_tree
class GeneticOperatorTests(unittest.TestCase):
    def test_mutation_validity(self):
        r=random.Random(103);g=random_genome(r);seen=set()
        for _ in range(500):
            g=structural_mutation(g,r);g.validate();seen.add(g.identity())
        self.assertGreater(len(seen),200)
    def test_nested_group_legal(self):
        a=leaf(random.Random(1));b=leaf(random.Random(2));c=leaf(random.Random(3))
        g=Genome({'op':'OR','children':[a,{'op':'AND','children':[b,c]}]})
        g.validate()
        features={(x['feature'],x['window'],x['transform']):x['threshold']+1 for x in (a,b,c)}
        self.assertTrue(score_tree(g.tree,features)[0])
    def test_crossover_validity(self):
        r=random.Random(104);a=random_genome(r);b=random_genome(r)
        seen=set()
        for _ in range(150):
            g=tree_crossover(a,b,r);g.validate();seen.add(g.identity())
        self.assertGreater(len(seen),5)
    def test_hard_cap(self):
        r=random.Random(105);g=random_genome(r)
        for _ in range(300):
            g=structural_mutation(g,r)
            self.assertLessEqual(g.hold_sessions,40)
            self.assertLessEqual(g.target_weight,.10)
if __name__=='__main__':unittest.main()
