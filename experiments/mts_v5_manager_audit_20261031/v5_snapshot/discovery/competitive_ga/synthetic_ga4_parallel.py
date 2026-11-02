"""Eight-process native GA4 predictor builder; original factory and cross-sectional code unchanged."""
import sys,json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import pandas as pd,numpy as np
ROOT=Path('/opt/mts/synthetic-market-lab')
BASE=Path('/opt/mts/thunder-migration/mts-layered-run-20261007')
sys.path.insert(0,str(BASE))
from Core.layered_ga.stage2_features_v3 import build_stock_local_frame,recompute_cross_sectional
from discovery.competitive_ga.synthetic_adapter import load_fsynth
def worker(task):
    ticker,frame,sector=task
    return build_stock_local_frame(frame,ticker,sector,None)
def build(i,workers=8):
    source=ROOT/f'runs/five_iteration_inputs/universe_{i}'
    frame=load_fsynth(source)
    sectors=pd.read_parquet(source/'stock_prices.parquet',columns=['Ticker','Sector']).drop_duplicates()
    if sectors.Ticker.duplicated().any():raise ValueError('sector mapping is not static')
    sector_map=dict(zip(sectors.Ticker,sectors.Sector))
    frame=frame.rename(columns={k:k.lower() for k in ('Date','Ticker','Open','High','Low','Close','Volume')})
    tasks=[(ticker,g,str(sector_map[ticker])) for ticker,g in frame.groupby('ticker',sort=True)]
    pieces=[]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures=[pool.submit(worker,t) for t in tasks]
        for j,future in enumerate(as_completed(futures),1):
            pieces.append(future.result())
            if j%100==0:print(f'universe {i}: {j}/500',flush=True)
    full=recompute_cross_sectional(pd.concat(pieces,ignore_index=True))
    for col in tuple(full.columns):
        if col.endswith('__v1'):
            full['ga4_'+col]=np.tanh(pd.to_numeric(full[col],errors='coerce').astype(float).clip(-1e8,1e8))
    full=full.rename(columns={'effective_date':'date'})
    full['date']=pd.to_datetime(full['date'])
    out=ROOT/f'runs/causal_native_features/universe_{i}_ga4_native.parquet'
    full.to_parquet(out,index=False)
    print(json.dumps({'universe':i,'rows':len(full),'ga4_columns':sum(c.startswith('ga4_') for c in full),'output':str(out)}),flush=True)
if __name__=='__main__':
    for i in [int(x) for x in sys.argv[1:]]:build(i)
