"""Real components, synthetic securities, no protected data or paid GA."""
import tempfile
import unittest
import numpy as np
import pandas as pd
from Core.layered_ga.ga4_fold_isolation import freeze_fold_membership
from Core.layered_ga.ga4_fold_runner import run_fold_discovery
from Core.layered_ga.ga4_catalog_store import read_records

class Gene:
    def __init__(self, name, values):
        self.gene_id=name
        self.values=values
class Space:
    genes=(Gene('momentum_feature',('return_20__v1',)), Gene('threshold_quantile',(0.25,0.5,0.75)), Gene('direction',('ABOVE','BELOW')), Gene('context_feature',('NONE',)), Gene('context_threshold',(0.0,)))

class TestSyntheticIntegration(unittest.TestCase):
    def test_real_fold_to_evolution_and_catalog(self):
        ids=[f'D{i:02d}' for i in range(80)]
        membership=freeze_fold_membership(ids,[f'H{i:02d}' for i in range(37)])
        dates=pd.bdate_range('2025-01-02',periods=95)
        rows=[]
        for k,security in enumerate(ids):
            for t,date in enumerate(dates):
                close=50+0.1*t+0.3*k+np.sin(t/8+k)*0.4
                rows.append({'security_id':security,'date':date,'effective_date':date,'sector_id':'S'+str(k%4),'open':close,'high':close*1.01,'low':close*.99,'close':close,'adj_close':close,'volume':1000000,'return_252__v1':0.001*k,'return_252_skip_20__v1':0.001*k,'return_126__v1':0.001*k,'relative_volume_20__v1':1.0,'natr_20__v1':0.02,'realized_vol_20__v1':0.2,'close_to_sma_200__v1':1.0,'return_20__v1':np.sin(t/8+k)*.01,'return_1__v1':0.001,'range_position_252__v1':0.5,'return_63__v1':0.01})
        frame=pd.DataFrame(rows)
        local=frame.drop(columns=['date','open','high','low','close','adj_close','volume'])
        raw=frame.drop(columns=['effective_date'])
        with tempfile.TemporaryDirectory() as folder:
            result=run_fold_discovery(stock_local=local,raw=raw,membership=membership,spaces={'MOMENTUM':Space()},context_factory=lambda f:(np.ones(len(f),dtype=bool),{'market':'synthetic'}),catalog_dir=folder,seed=3,population_size=2,generations=2)
            records=read_records(folder)
            self.assertGreaterEqual(len(records),1)
            self.assertEqual(len(records),result['unique_evaluations'])
            self.assertTrue(all(len(x['daily_horizon_evidence'])==63 for x in records))
            self.assertTrue(all(x['fold']=='DEV80' and not x['certified'] for x in records))
            self.assertEqual(len(result['generations']),2)

if __name__=='__main__':unittest.main()

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]