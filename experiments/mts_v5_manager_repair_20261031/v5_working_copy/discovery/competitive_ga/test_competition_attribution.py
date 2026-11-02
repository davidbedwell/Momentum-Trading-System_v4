import unittest
from discovery.competitive_ga.competition_attribution import Event,summarize
class TestAttribution(unittest.TestCase):
 def test_family_wins_and_profit(self):
  events=[Event('2020-06-01','A','a','NICHE','SELECTED','NICHE-0001'),Event('2020-06-02','A','a','NICHE','CLOSED','NICHE-0001',25),Event('2020-06-01','B','b','HORIZONS','SELECTED'),Event('2020-06-02','B','b','HORIZONS','CLOSED',net_profit=100),Event('2020-06-02','C','c','GA4','CLOSED',net_profit=50,shadow=True)]
  x=summarize(events)
  self.assertEqual(x['families']['HORIZONS']['realized_profit'],100)
  self.assertEqual(x['families']['GA4']['shadow_profit'],50)
  self.assertEqual(x['niches']['NICHE-0001']['selected'],1)
 def test_reject_fake_shadow_fill(self):
  with self.assertRaises(ValueError):Event('2020-06-01','A','a','GA4','FILLED',shadow=True)
if __name__=='__main__':unittest.main()
