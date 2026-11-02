import unittest
from .daily_shadow_training import DailyShadowTrainer, ShadowPrediction
class TestDailyShadow(unittest.TestCase):
 def test_no_early_learning(self):
  t=DailyShadowTrainer();p=ShadowPrediction(0,'SYN1','a','NICHE',.1,2)
  t.record_close(0,[p]);t.record_close(1,[])
  self.assertEqual(t.mature(1,{(0,'SYN1','a'):.2}),0)
  self.assertEqual(t.weights,{})
  t.record_close(2,[]);self.assertEqual(t.mature(2,{(0,'SYN1','a'):.2}),1)
  self.assertEqual(t.weights[('NICHE','a')]['mean_net_return'],.2)
 def test_chronological(self):
  t=DailyShadowTrainer();t.record_close(1,[])
  with self.assertRaises(ValueError):t.record_close(1,[])
if __name__=='__main__':unittest.main()
