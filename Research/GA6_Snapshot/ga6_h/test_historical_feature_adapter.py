import unittest
from context_free_genome import Genome
from historical_feature_adapter import score_session
class FeatureTests(unittest.TestCase):
 def test_causal_momentum(self):
  g=Genome({'op':'AND','children':[{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'volume','window':20,'threshold':0,'direction':'>=','transform':'raw'}]})
  rows=[{'symbol':'A','return_20':.1,'volume_ratio_20':1.2,'forward_adj_return_20':-1},{'symbol':'B','return_20':-.1,'volume_ratio_20':1.2,'forward_adj_return_20':1}]
  self.assertEqual([r['symbol'] for r in score_session(g,rows)],['A'])
 def test_missing_feature_no_trade(self):
  g=Genome({'op':'AND','children':[{'feature':'breadth','window':20,'threshold':0,'direction':'>=','transform':'raw'},{'feature':'momentum','window':20,'threshold':0,'direction':'>=','transform':'raw'}]})
  self.assertEqual(score_session(g,[{'symbol':'A','return_20':.1}]),[])
