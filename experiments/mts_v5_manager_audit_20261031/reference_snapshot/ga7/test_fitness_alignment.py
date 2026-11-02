import unittest
from ga7.engine import breeding_eligible, dominates, add_behavioral_diversity
from ga7.stagnation import update_stagnation
class FitnessAlignmentTests(unittest.TestCase):
 def test_no_cagr_mdd_gate(self):
  self.assertTrue(breeding_eligible({'trades':6,'conservative_ev_r':.2,'cagr':-.1,'mdd':.8}))
  self.assertFalse(breeding_eligible({'trades':6,'conservative_ev_r':-.01}))
 def test_pareto_r_mae_diversity(self):
  a={'conservative_ev_r':.3,'mae_stop_ratio':.4,'behavioral_diversity':.5}
  b={'conservative_ev_r':.2,'mae_stop_ratio':.5,'behavioral_diversity':.3}
  self.assertTrue(dominates(a,b))
  self.assertFalse(dominates(b,a))
 def test_behavior_novelty(self):
  s=[(None,{'entry_signature':['a','b']}),(None,{'entry_signature':['a','b']}),(None,{'entry_signature':['c']}),(None,{'entry_signature':[]})]
  add_behavioral_diversity(s)
  self.assertGreater(s[2][1]['behavioral_diversity'],s[0][1]['behavioral_diversity'])
  self.assertEqual(s[3][1]['behavioral_diversity'],0)
 def test_stagnation_uses_r_and_mae(self):
  m={'trades':10,'ev_r':.4,'conservative_ev_r':.4,'mae_stop_ratio':.3,'behavioral_diversity':.5}
  _,_,improved=update_stagnation([m],[],0)
  self.assertTrue(improved)
if __name__=='__main__':unittest.main()
