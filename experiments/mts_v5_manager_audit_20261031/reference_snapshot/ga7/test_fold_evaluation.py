import unittest
from ga7.fold_evaluation import summarize_forward,replay_fold
class FoldEvaluationTests(unittest.TestCase):
 def test_forward_summary(self):
  m={'trades':6,'conservative_ev_r':.2,'mae_stop_ratio':.8}
  r=summarize_forward([m,{**m,'conservative_ev_r':-.1}])
  self.assertEqual(r['positive_windows'],1)
  self.assertEqual(r['worst_conservative_ev_r'],-.1)
 def test_invalid_phase(self):
  with self.assertRaises(ValueError):replay_fold(None,[],None,{},[],'breeding')
if __name__=='__main__':unittest.main()
