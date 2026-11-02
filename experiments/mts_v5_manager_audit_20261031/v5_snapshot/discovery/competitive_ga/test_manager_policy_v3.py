import unittest
from .manager_policy_v3 import decide
from .manager_policy_v2 import Proposal,Genes

def p(t,a,edge,target=.1):
 return Proposal(t,a,'GA6',a,edge,0.,1.,target,True,20)
class TestManagerPolicy(unittest.TestCase):
 def test_hold_beats_weak_exit(self):
  self.assertNotIn('A',decide([p('A','HOLD',.05),p('A','EXIT',.01,0)],{'A':.1},.2,Genes(max_total=.1)))
 def test_better_exit_can_win(self):
  self.assertEqual(decide([p('A','HOLD',.01),p('A','EXIT',.08,0)],{'A':.1},.2,Genes(max_total=.1))['A'][0],'EXIT')
 def test_cash_not_reused_on_exit(self):
  out=decide([p('A','EXIT',.1,0),p('B','ENTER',.2)],{'A':.1},0.,Genes(max_total=.1))
  self.assertEqual(out['A'][0],'EXIT')
  self.assertNotIn('B',out)
 def test_no_forced_horizon(self):
  self.assertNotIn('A',decide([p('A','HOLD',.1)],{'A':.1},0.,Genes(max_total=.1)))
if __name__=='__main__':unittest.main()
