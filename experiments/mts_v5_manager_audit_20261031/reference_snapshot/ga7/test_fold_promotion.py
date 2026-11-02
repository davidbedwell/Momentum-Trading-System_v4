import unittest
from ga7.fold_promotion import freeze_cohort
from ga7.engine import Genome
class PromotionTests(unittest.TestCase):
 def test_frozen_hash(self):
  g=Genome('momentum','a','b','AND',0,0,.05,3,'reversal',.02)
  x=freeze_cohort({'NON_NICHE':[(g,{'conservative_ev_r':.2,'mae_stop_ratio':.5})]})
  self.assertEqual(x['sha256'],freeze_cohort({'NON_NICHE':[(g,{'conservative_ev_r':.2,'mae_stop_ratio':.5})]})['sha256'])
if __name__=='__main__':unittest.main()
