"""Rebuild archived GA4 feature definitions on synthetic OHLCV using the original factory.
Research only; does not assert production PIT certification.
"""
import sys,json
from pathlib import Path
import pandas as pd
import numpy as np
BASE=Path('/opt/mts/thunder-migration/mts-layered-run-20261007')
sys.path.insert(0,str(BASE))
from Core.layered_ga.stage2_features_v3 import build_stock_local_frame,recompute_cross_sectional
from discovery.competitive_ga.synthetic_adapter import load_fsynth
ROOT=Path('/opt/mts/synthetic-market-lab')
OUT=ROOT/'runs/causal_native_features'
def build(i):
    source=ROOT/f'runs/five_iteration_inputs/universe_{i}'
    frame=load_fsynth(source)
    sectors=pd.read_parquet(source/'stock_prices.parquet',columns=['Ticker','Sector']).drop_duplicates()
    if sectors.Ticker.duplicated().any():raise ValueError('nonstatic sector requires PIT mapping')
    sector_map=dict(zip(sectors.Ticker,sectors.Sector))
    frame=frame.rename(columns={k:k.lower() for k in ('Date','Ticker','Open','High','Low','Close','Volume')})
    pieces=[]
    for j,(ticker,g) in enumerate(frame.groupby('ticker',sort=True)):
        pieces.append(build_stock_local_frame(g,ticker,str(sector_map[ticker]),None))
        if (j+1)%100==0:print(f'universe {i}: {j+1} of 500 stock-local predictors',flush=True)
    full=recompute_cross_sectional(pd.concat(pieces,ignore_index=True))
    original=full.copy()
    for col in tuple(full.columns):
        if col.endswith('__v1'):
            full['ga4_'+col]=np.tanh(pd.to_numeric(full[col],errors='coerce').astype(float).clip(-1e8,1e8))
    full=full.rename(columns={'effective_date':'date'})
    full['date']=pd.to_datetime(full['date'])
    out=OUT/f'universe_{i}_ga4_native.parquet'
    full.to_parquet(out,index=False)
    print(json.dumps({'universe':i,'rows':len(full),'ga4_columns':sum(c.startswith('ga4_') for c in full),'output':str(out)}),flush=True)
if __name__=='__main__':
    for i in [int(x) for x in sys.argv[1:]]:build(i)
