import unittest
from ga6.upgrade_reuse_20261021.scientific_selection import eligible,truncate,niche_archive
C={'min_trades':30,'min_adjusted_ev':0,'min_trades_per_year':10,'max_expected_shortfall':.2,'max_drawdown':.35,'min_stability':.6}
E={'completed_trades':100,'net_ev_lcb_adjusted':.01,'trades_per_year':20,'capital_time_efficiency':.2,'expected_shortfall':-.1,'max_drawdown':-.2,'stability_fraction':.9,'multiplicity_verified':True,'costs_verified':True,'oos_verified':True}
class ScientificTests(unittest.TestCase):
 def test_missing_is_rejected(self):self.assertFalse(eligible({'completed_trades':500},C)[0])
 def test_positive_ev_not_enough(self):
  e={**E,'multiplicity_verified':False};self.assertFalse(eligible(e,C)[0])
 def test_three_objective_determinism(self):
  items=[(str(i),{**E,'net_ev_lcb_adjusted':i*.001+.001,'capital_time_efficiency':.3-i*.001,'expected_shortfall':-.1+i*.0001}) for i in range(30)]
  self.assertEqual(truncate(items,10),truncate(list(reversed(items)),10))
  self.assertEqual(len(truncate(items,10)),10)
 def test_rejected_retained(self):
  a,r=niche_archive([('ok','n',E),('bad','n',{**E,'oos_verified':False})],C)
  self.assertEqual(a['n'],['ok']);self.assertEqual(len(r),1)
if __name__=='__main__':unittest.main()
