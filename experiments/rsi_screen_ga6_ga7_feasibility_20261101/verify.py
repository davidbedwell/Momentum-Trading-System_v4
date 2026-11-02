"""Independent cash/share replay from exported fills and original price marks."""
import json
from pathlib import Path
import pandas as pd
import numpy as np
P=Path(__file__).resolve().parent
raw=pd.read_parquet('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet',columns=['date','ticker','close'],filters=[('date','>=',pd.Timestamp('2009-01-01')),('date','<',pd.Timestamp('2019-01-01'))]);raw.date=pd.to_datetime(raw.date).dt.strftime('%Y-%m-%d')
marks={(d,t):c for d,t,c in raw.itertuples(index=False,name=None)}
sel=pd.read_csv(P.parent/'dev79_rsi_indicator_combinations_20261101/selections.csv');sel=sel[sel.strategy.eq('k2_2-4')];allowed={(d[:7],t) for d,t in zip(sel.execution_date,sel.ticker)}
result={}
for mode in ('fixed','ga7'):
 fills=pd.read_csv(P/mode/'fills.csv');daily=pd.read_csv(P/mode/'daily.csv');cash=100000.;due=0.;q={};maxerr=0.;groups={d:g for d,g in fills.groupby('date')};days=list(daily.date)
 for i,row in daily.iterrows():
  d=row.date;cash+=due;due=0.
  if d in groups:
   for f in groups[d].itertuples():
    assert f.signal_date<d
    if mode=='ga7':
     assert i>0 and f.signal_date==days[i-1]
     if f.side=='BUY':assert (d[:7],f.ticker) in allowed
    assert abs(f.fee-f.shares*f.price*.0005)<1e-7
    assert abs(f.price/f.open-(1.0005 if f.side=='BUY' else .9995))<1e-12
    if f.side=='BUY':cash-=f.shares*f.price+f.fee;q[f.ticker]=q.get(f.ticker,0.)+f.shares
    else:
     assert f.shares<=q[f.ticker]+1e-8
     due+=f.shares*f.price-f.fee;q[f.ticker]-=f.shares
     if q[f.ticker]<1e-9:del q[f.ticker]
    assert cash>=-1e-7
  nav=cash+due+sum(qty*marks[(d,t)] for t,qty in q.items());maxerr=max(maxerr,abs(nav-row.nav))
  assert abs(nav-row.nav)<1e-6
 v=np.r_[100000.,daily.nav];cagr=(v[-1]/v[0])**(252/len(daily))-1;mdd=float((1-v/np.maximum.accumulate(v)).max())
 metrics=json.loads((P/'metrics.json').read_text())[mode]
 assert abs(cagr-metrics['cagr'])<1e-12 and abs(mdd-metrics['mdd'])<1e-12
 result[mode]=dict(independent_max_nav_error=maxerr,fill_count=len(fills),causal_fills=True,cost_formulas=True,screened_buys=True if mode=='ga7' else None)
result['status']='PASS'
(P/'verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
