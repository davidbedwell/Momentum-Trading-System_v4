"""Validate completed expansion artifacts without reading sealed source periods."""
import json
import math
from pathlib import Path
import numpy as np
import pandas as pd
from . import core
from .expanded_stage1 import OUT, ROOT, sha


def run():
    report=json.loads((OUT/'report.json').read_text())
    assert report['status'].startswith('COMPLETED')
    assert report['protected_hashes_before']==report['protected_hashes_after']
    assert all(sha(ROOT/p)==h for p,h in report['protected_hashes_before'].items())
    prices=pd.read_parquet(OUT/'prices_used.parquet')
    assert len(prices)==report['price_rows'] and prices.symbol.nunique()==report['cached_stage1_symbols']
    assert prices.date.min()>='2004-01-01' and prices.date.max()<='2015-12-31'
    assert not prices.duplicated(['symbol','date']).any()
    members=pd.read_csv(OUT/'membership_used.csv',keep_default_na=False)
    assert (members.start==members.sector_evidence_date).all()
    assert not members.duplicated(['symbol','start']).any()
    assert all(sha(ROOT/s['path'])==s['sha256'] for s in report['sources'])
    checks={}
    for name,scenario in report['scenarios'].items():
        rows=pd.read_parquet(OUT/name/'observations.parquet')
        assert len(rows)==scenario['available_stock_benchmark_rows'] and len(rows)>0
        assert not rows.duplicated(['symbol','asof','horizon']).any()
        assert rows['asof'].min()>='2006-01-01' and rows['asof'].max()<='2015-12-31'
        assert rows.exit.max()<='2015-12-31' and (rows.entry>rows['asof']).all()
        assert np.isfinite(rows.forward_return).all()
        assert not (rows.sector=='UNKNOWN').any()
        # Independently recompute an observed sector Spearman IC from saved ranked observations.
        monthly=pd.read_csv(OUT/name/'monthly_metrics.csv')
        tested=0
        for _,m in monthly[monthly.ic.notna()].groupby(['signal','horizon']).head(1).iterrows():
            g=rows[(rows['asof']==m['asof'])&(rows.sector==m.sector)&(rows.horizon==m.horizon)]
            g=g[g[m.signal+'_rank'].notna()]
            observed=core.ic(g[m.signal+'_rank'].tolist(),g.excess.tolist())
            assert math.isclose(observed,m.ic,abs_tol=1e-12)
            tested+=1
        for k,v in scenario['summary'].items():
            p=v['placebo']
            assert p['shuffles']==(1000 if v['mean'] is not None else 0)
            if v['mean'] is not None:
                direction=-1 if k.startswith('H5') else 1
                assert math.isclose(v['mean']*direction,p['real'],abs_tol=1e-12)
            assert v['certified_pass'] is False
        checks[name]=dict(observation_rows=len(rows),independently_recomputed_sector_ics=tested,
                          defined_statistics=sum(v['mean'] is not None for v in scenario['summary'].values()))
    validation=dict(status='PASS',sealed_hashes_unchanged=True,no_stage2_rows=True,source_hashes_verified=True,
                    price_rows=len(prices),priced_symbols=prices.symbol.nunique(),scenarios=checks)
    (OUT/'validation.json').write_text(json.dumps(validation,indent=2))
    print(json.dumps(validation,indent=2))
    return validation

if __name__=='__main__':run()
