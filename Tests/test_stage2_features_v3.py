import numpy as np,pandas as pd
from Core.layered_ga.stage2_features_v3 import _raw_records,_source_factory,build_stock_local_frame,recompute_cross_sectional,CROSS_COLUMNS

def raw_fixture():
    rows=[]
    dates=pd.bdate_range('2024-01-02',periods=310)
    for j,(t,sector) in enumerate([('A','S1'),('B','S1'),('C','S2')]):
        base=50+10*j
        close=base*np.exp((.0002+.0001*j)*np.arange(len(dates)) + .01*np.sin(np.arange(len(dates))/7+j))
        for i,dt in enumerate(dates):
            c=close[i];rows.append({'security_id':t,'date':dt,'open':c*.999,'high':c*1.01,'low':c*.99,'close':c,'volume':1_000_000+1000*i+10000*j,'eligible':True,'ticker':t,'sector_id':sector,'industry_id':'I'})
    return pd.DataFrame(rows)

def test_parallel_reconstruction_matches_monolithic_cross_sectional_factory():
    raw=raw_fixture();factory=_source_factory();oracle=pd.DataFrame(factory(raw.to_dict('records'))).sort_values(['effective_date','security_id']).reset_index(drop=True)
    parts=[]
    for t,g in raw.groupby('security_id'):
        slim=g.rename(columns={}).copy(); # adapt to helper's expected market-frame columns
        parts.append(build_stock_local_frame(slim,t,g.sector_id.iloc[0],'I'))
    got=recompute_cross_sectional(pd.concat(parts,ignore_index=True))
    oracle['effective_date']=pd.to_datetime(oracle.effective_date)
    for col in CROSS_COLUMNS:
        a=pd.to_numeric(oracle[col],errors='coerce').to_numpy(float);b=pd.to_numeric(got[col],errors='coerce').to_numpy(float)
        assert np.allclose(a,b,equal_nan=True,rtol=0,atol=1e-12),col
