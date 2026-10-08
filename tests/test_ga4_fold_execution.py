[Reading 28 lines from start (total: 28 lines, 0 remaining)]

import unittest
from unittest.mock import patch
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_fold_execution import build_discovery_execution
from Core.layered_ga.stage2_path_v3 import ExecutionPaths, ProspectiveCosts

class TestFoldExecution(unittest.TestCase):
    def test_full_history_projected_in_decision_order(self):
        pred=pd.DataFrame({'security_id':['B','A'],'effective_date':['2026-01-02']*2})
        raw=pd.DataFrame({'security_id':['A','A','B','B'],'date':pd.to_datetime(['2026-01-01','2026-01-02']*2)})
        matrix=np.tile(np.arange(4)[:,None],(1,63)).astype(float)
        paths=ExecutionPaths(matrix,matrix,matrix,matrix)
        costs=ProspectiveCosts(matrix,matrix,np.arange(4),np.arange(4),np.arange(4),np.arange(4))
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(pred,raw,'scope')):
            with patch('Core.layered_ga.stage2_path_v3.build_execution_paths',return_value=paths) as path_builder:
                with patch('Core.layered_ga.stage2_path_v3.build_prospective_costs',return_value=costs):
                    result=build_discovery_execution(None,None,None)
        self.assertEqual(list(result[1].endpoint_return[:,0]),[3,1])
        self.assertEqual(list(result[2].spread_bps),[3,1])
        self.assertEqual(len(path_builder.call_args.args[0]),4)
        self.assertEqual(result[4],'scope')
    def test_missing_decision_identity_rejected(self):
        pred=pd.DataFrame({'security_id':['A'],'effective_date':['2026-01-02']})
        raw=pd.DataFrame({'security_id':['A'],'date':['2026-01-01']})
        with patch('Core.layered_ga.ga4_fold_execution.prepare_discovery_frame',return_value=(pred,raw,'scope')):
            with self.assertRaises(ValueError):build_discovery_execution(None,None,None)
if __name__=='__main__':unittest.main()

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]