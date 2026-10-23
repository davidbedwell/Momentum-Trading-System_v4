import unittest
from ga5_redesign.niche_seeds import initial
from ga5_chromosome_decisions import PositionState
from ga6.structural_independent_v2_20261022.structural_decision import decision
from fast_decision import evaluate as legacy
class StructuralDecisionTests(unittest.TestCase):
 def setUp(self):
  self.g=initial('NICHE-0001')
  self.f={k:1.0 for k in (self.g.entry_feature,self.g.regime_feature,self.g.sizing_feature,self.g.hold_feature,self.g.exit_feature,self.g.replace_feature)}
  self.f.update({'trend':.5,'momentum':.5,'volume':-.5})
  self.p=PositionState()
 def test_legacy_unchanged_without_tree(self):
  self.assertEqual(decision(self.g,self.f,self.p,100),legacy(self.g,self.f,self.p,100))
 def test_and_or_different(self):
  leaves=[{'family':x,'threshold':0.,'comparison':'>='} for x in ('trend','volume')]
  self.assertEqual(decision(self.g,self.f,self.p,100,{'op':'AND','children':leaves})[0],'NO_ENTRY')
  self.assertEqual(decision(self.g,self.f,self.p,100,{'op':'OR','children':leaves})[0],'ENTER')
 def test_missing_feature_blocks_entry(self):
  tree={'op':'AND','children':[{'family':'trend','threshold':0,'comparison':'>='},{'family':'breadth','threshold':0,'comparison':'>='}]}
  self.assertEqual(decision(self.g,self.f,self.p,100,tree)[0],'NO_ENTRY')
 def test_exits_unmodified(self):
  p=PositionState(10,100,110,2)
  tree={'op':'AND','children':[{'family':'trend','threshold':0,'comparison':'>='},{'family':'breadth','threshold':0,'comparison':'>='}]}
  self.assertEqual(decision(self.g,self.f,p,80,tree),legacy(self.g,self.f,p,80))
if __name__=='__main__':unittest.main()
