import unittest,json
from ga5_redesign.niche_seeds import initial
from ga6.structural_evolution_v3_20261022.structural_candidate import StructuralCandidate
class CandidateTests(unittest.TestCase):
 def setUp(self):
  self.g=initial('NICHE-0001')
  self.leaves=[{'family':f,'threshold':0,'comparison':'>='} for f in ('trend','momentum')]
 def test_structural_identity_changes_with_logic(self):
  a=StructuralCandidate(self.g,{'op':'AND','children':self.leaves})
  b=StructuralCandidate(self.g,{'op':'OR','children':self.leaves})
  self.assertNotEqual(a.identity(),b.identity())
 def test_checkpoint_round_trip(self):
  a=StructuralCandidate(self.g,{'op':'AND','children':self.leaves})
  self.assertEqual(StructuralCandidate.restore(json.loads(json.dumps(a.checkpoint()))),a)
 def test_tampering_rejected(self):
  a=StructuralCandidate(self.g,{'op':'AND','children':self.leaves})
  state=a.checkpoint();state['entry_tree']['op']='OR'
  with self.assertRaises(ValueError):StructuralCandidate.restore(state)
 def test_invalid_expression_rejected(self):
  with self.assertRaises(ValueError):StructuralCandidate(self.g,{'op':'X','children':self.leaves})
if __name__=='__main__':unittest.main()
