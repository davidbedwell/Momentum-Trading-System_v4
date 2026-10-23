"""Frozen B1 standalone causal signal audit; no portfolio changes."""
import json, pathlib, sys
import pandas as pd
ROOT=pathlib.Path('/opt/mts')
sys.path.insert(0,str(ROOT/'thunder-migration/mts-certification-20261011/repair_20261012/scripts'))
from causal_percentile_adapter import causal_funding_percentiles
OUT=ROOT/'ga6/data/ofr_b1'
ofr=pd.read_csv(OUT/'ofr_fsi_20261022.csv',parse_dates=['Date']).set_index('Date').sort_index()
spy_path=ROOT/'thunder-migration/Momentum-Trading-System_v4/Research/Data/Comparators/SPY_20050901_20260914_20261006.csv'
spy=pd.read_csv(spy_path,header=[0,1],index_col=0,parse_dates=True)
close=pd.to_numeric(spy[('Close','SPY')],errors='coerce').dropna()
close=close[~close.index.duplicated()].sort_index()
missing=close.index.difference(ofr.index)
print("OFR_MISSING_SPY_DATES",[str(x.date()) for x in missing],flush=True)
fund=ofr.Funding.reindex(ofr.index.union(close.index)).sort_index().ffill().reindex(close.index)
assert fund.notna().all(), 'Missing OFR values on SPY trading sessions'
pct=causal_funding_percentiles(fund.tolist())['funding_pct']
tape=pd.DataFrame({'spy_close':close,'funding_observed':fund,'funding_pct_lag2':pct},index=close.index)
tape['sma200']=close.rolling(200,min_periods=200).mean()
tape['below200']=close.lt(tape.sma200)
tape['below200_10']=tape.below200.rolling(10,min_periods=10).sum().eq(10)
tape['b1_active']=tape.below200_10 & tape.funding_pct_lag2.ge(.70)
tape['b1_rising']=tape.b1_active & ~tape.b1_active.shift(1,fill_value=False)
tape.to_csv(OUT/'B1_CAUSAL_DAILY_TAPE.csv',index_label='date')
windows=[('GFC','2007-10-09','2009-03-09'),('COVID','2020-02-19','2020-03-23'),('2011_2015','2011-01-01','2015-12-31'),('2021_2024','2021-01-01','2024-12-31')]
results={}
for name,start,end in windows:
 z=tape.loc[start:end]
 active=z.index[z.b1_active]
 entries=z.index[z.b1_rising]
 results[name]={'sessions':len(z),'active_sessions':len(active),'first_active':str(active.min().date()) if len(active) else None,'entry_dates':[str(d.date()) for d in entries],'last_active':str(active.max().date()) if len(active) else None,'below200_10_sessions':int(z.below200_10.sum()),'funding_ge_70_sessions':int(z.funding_pct_lag2.ge(.7).sum())}
print(json.dumps(results,indent=2))
(OUT/'B1_AUDIT.json').write_text(json.dumps({'spec':'SPY below trailing 200-session SMA for 10 consecutive sessions AND lagged OFR Funding 252-session rolling percentile >=0.70; 126 min observations','source':'OFR FSI historical revised download; not point-in-time vintage','execution':'signal only; no portfolio replay; decision at close; earliest action next open','windows':results},indent=2))
