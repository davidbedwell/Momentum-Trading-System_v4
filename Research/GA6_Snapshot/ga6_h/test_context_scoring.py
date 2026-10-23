import unittest
from context_free_genome import Genome
from context_scoring import score_tree,evaluate_contexts
A={'feature':'momentum','window':5,'threshold':0.1,'direction':'>=','transform':'raw'}
B={'feature':'momentum','window':60,'threshold':0.0,'direction':'<=','transform':'raw'}
T={'op':'AND','children':[A,B]}
class ContextTests(unittest.TestCase):
    def test_same_genome_multiple_contexts(self):
        g=Genome(T)
        features={('momentum',5,'raw'):0.2,('momentum',60,'raw'):-0.1}
        result=evaluate_contexts(g,[('uptrend','AAA',features),('other','BBB',features)])
        self.assertEqual(result['uptrend']['passed'],1)
        self.assertEqual(result['other']['passed'],1)
        self.assertEqual(len(g.identity()),64)
    def test_missing_fail_closed(self):
        self.assertIsNone(score_tree(T,{('momentum',5,'raw'):0.2}))
    def test_and_logic(self):
        self.assertTrue(score_tree(T,{('momentum',5,'raw'):0.2,('momentum',60,'raw'):-0.1})[0])
        self.assertFalse(score_tree(T,{('momentum',5,'raw'):0.2,('momentum',60,'raw'):0.3})[0])
    def test_or_logic(self):
        t={'op':'OR','children':[A,B]}
        self.assertTrue(score_tree(t,{('momentum',5,'raw'):0.2,('momentum',60,'raw'):0.3})[0])
if __name__=='__main__':unittest.main()
