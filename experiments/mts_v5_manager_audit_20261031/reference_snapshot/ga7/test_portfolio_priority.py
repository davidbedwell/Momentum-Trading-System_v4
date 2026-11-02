import unittest
from ga7.portfolio_priority import prioritize_pending
from ga7.proposals import Proposal
class PortfolioPriorityTests(unittest.TestCase):
 def p(self,ticker,action,score):
  return Proposal(1,ticker,'g',action,score,score*.1,.02,.05 if action=='ENTER' else 0,0,score)
 def test_exit_precedes_entries(self):
  items=[self.p('Z','ENTER',.99),self.p('X','EXIT',.01),self.p('A','ENTER',.60)]
  self.assertEqual([x.ticker for x in prioritize_pending(items)],['X','Z','A'])
 def test_deterministic_across_input_order(self):
  items=[self.p('Z','ENTER',.6),self.p('A','ENTER',.6)]
  self.assertEqual(prioritize_pending(items),prioritize_pending(items[::-1]))
if __name__=='__main__':unittest.main()
