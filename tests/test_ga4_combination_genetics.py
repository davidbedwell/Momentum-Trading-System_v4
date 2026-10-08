import random
import unittest
from Core.layered_ga.ga4_combination_genetics import validate,combine,propose
class Gene:
    def __init__(self): self.gene_id='x'; self.values=(1,2,3,4,5)
class Space:
    genes=(Gene(),)
class TestCombinations(unittest.TestCase):
    def test_bounded_proposals(self):
        rng=random.Random(13)
        for _ in range(50):
            value=propose({'A':Space(),'B':Space()},rng)
            self.assertTrue(1<=len(value)<=4)
            validate(value)
    def test_recombination(self):
        rng=random.Random(4)
        a=(('A',{'x':1}),('A',{'x':2}))
        b=(('B',{'x':3}),('B',{'x':4}))
        for _ in range(20): validate(combine(a,b,rng))
    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError): validate((('A',{'x':1}),('A',{'x':1})))
if __name__=='__main__': unittest.main()
