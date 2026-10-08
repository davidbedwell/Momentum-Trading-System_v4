[Reading 27 lines from start (total: 27 lines, 0 remaining)]

"""Regression: warmup and post-decision bars must survive projection."""
import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_fold_execution import build_discovery_execution

class TestFullHistoryOutcomes(unittest.TestCase):
    def test_63_day_forward_and_20_day_adv_survive(self):
        dates=pd.bdate_range('2026-01-02',periods=110)
        raw=pd.DataFrame([{'security_id':s,'date':day,'open':100+i,'high':101+i,'low':99+i,'close':100+i,'adj_close':100+i,'volume':1000000} for s in ['A','B'] for i,day in enumerate(dates)])
        predictors=pd.DataFrame({'security_id':['B','A'],'effective_date':[dates[30],dates[30]]})
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(predictors,raw,'scope')):
            pred,paths,costs,clusters,scope=build_discovery_execution(None,None,None)
        self.assertEqual(paths.endpoint_return.shape,(2,63))
        self.assertTrue(np.isfinite(paths.endpoint_return[:,62]).all())
        self.assertTrue(np.isfinite(costs.adv_dollars).all())
        self.assertTrue(np.isfinite(costs.long_roundtrip[:,62]).all())
        expected=(100+30+1+63)/(100+30+1)-1
        np.testing.assert_allclose(paths.endpoint_return[:,62],expected,rtol=1e-6)
    def test_predictor_after_history_rejected(self):
        dates=pd.bdate_range('2026-01-02',periods=80)
        raw=pd.DataFrame({'security_id':['A']*80,'date':dates})
        pred=pd.DataFrame({'security_id':['A'],'effective_date':[dates[-1]+pd.Timedelta(days=1)]})
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(pred,raw,'scope')):
            with self.assertRaises(ValueError):build_discovery_execution(None,None,None)
if __name__=='__main__':unittest.main()

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]