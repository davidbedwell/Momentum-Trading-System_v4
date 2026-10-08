import unittest
from unittest.mock import patch
import pandas as pd
from Core.layered_ga.ga4_fold_isolation import freeze_fold_membership
from Core.layered_ga.ga4_discovery_inputs import prepare_discovery_frame

class TestAssembly(unittest.TestCase):
    def setUp(self):
        self.membership=freeze_fold_membership([f'D{i}' for i in range(80)],[f'H{i}' for i in range(37)])
        self.predictors=pd.DataFrame({'security_id':self.membership['dev80'],'effective_date':['2026-01-02']*80})
        self.raw=pd.DataFrame({'security_id':self.membership['dev80']+self.membership['dev37'],'date':['2026-01-02']*117})
    def test_reorders_and_excludes_heldout(self):
        with patch('Core.layered_ga.ga4_discovery_inputs.rebuild_fold_predictors',return_value=(self.predictors,'scope')):
            pred,raw,scope=prepare_discovery_frame(None,self.raw.sample(frac=1,random_state=5),self.membership)
        self.assertEqual(list(pred.security_id),list(raw.security_id))
        self.assertEqual(len(raw),80)
    def test_rejects_missing_row(self):
        with patch('Core.layered_ga.ga4_discovery_inputs.rebuild_fold_predictors',return_value=(self.predictors,'scope')):
            with self.assertRaises(ValueError):prepare_discovery_frame(None,self.raw.iloc[1:],self.membership)
    def test_rejects_heldout_search(self):
        with self.assertRaises(ValueError):prepare_discovery_frame(None,self.raw,self.membership,phase='DEV37')

if __name__=='__main__': unittest.main()
