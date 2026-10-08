import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_fold_execution import build_discovery_execution

class TestFoldExecution(unittest.TestCase):
    def test_path_cost_cluster_alignment(self):
        ids=['A','B']
        pred=pd.DataFrame({'security_id':ids,'effective_date':['2026-01-01']*2})
        raw=pd.DataFrame({'security_id':ids,'date':['2026-01-01']*2})
        class Paths: endpoint_return=np.zeros((2,63))
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(pred,raw,'scope')):
            with patch('Core.layered_ga.stage2_path_v3.build_execution_paths',return_value=Paths()) as paths:
                with patch('Core.layered_ga.stage2_path_v3.build_prospective_costs',return_value='costs'):
                    result=build_discovery_execution(None,None,None)
        self.assertEqual(list(result[3]),[0,1])
        self.assertEqual(result[4],'scope')
        self.assertEqual(paths.call_args.kwargs['max_horizon'],63)
    def test_misaligned_rows_rejected(self):
        pred=pd.DataFrame({'security_id':['A','B'],'effective_date':['2026-01-01']*2})
        raw=pd.DataFrame({'security_id':['B','A']})
        class Paths: endpoint_return=np.zeros((2,63))
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(pred,raw,'scope')):
            with patch('Core.layered_ga.stage2_path_v3.build_execution_paths',return_value=Paths()):
                with patch('Core.layered_ga.stage2_path_v3.build_prospective_costs',return_value='costs'):
                    with self.assertRaises(ValueError):build_discovery_execution(None,None,None)
if __name__=='__main__':unittest.main()
