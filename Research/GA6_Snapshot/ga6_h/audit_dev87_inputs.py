import json
from pathlib import Path
import pandas as pd
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
r=Path('/opt/mts')
a=pd.read_parquet(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')
b=pd.read_parquet(r/'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet')
pa=json.loads((r/'ga5_redesign/exploratory79_policy.json').read_text())
pb=json.loads((r/'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_policy.json').read_text())
state=build_revised_daily_state().set_index('date')
state.index=state.index.strftime('%Y-%m-%d')
for name,f,p,start,end in [('development',a,pa,'2019-01-01','2025-01-01'),('DEV87',b,pb,'2025-01-01','2026-09-15')]:
 f=f[(f.date>=start)&(f.date<end)]
 dates=sorted(f.date.dt.strftime('%Y-%m-%d').unique())
 defens=sum(bool(state.loc[dates[i-1],'defensive']) for i in range(1,len(dates)))
 blocks=sum(len(set(p['blocked'].get(t,[]))&set(dates)) for t in f.ticker.unique())
 print(name,'sessions',len(dates),'years',round(len(dates)/252,3),'rows',len(f),'tickers',f.ticker.nunique(),'defensive_lagged_sessions',defens,'defensive_fraction',round(defens/max(1,len(dates)-1),3),'earnings_blocked_ticker_sessions',blocks,'block_fraction',round(blocks/(len(dates)*f.ticker.nunique()),4),'cash_yield',p['cash_proxy_annual_yield'])
 print('DATE',dates[0],dates[-1])
print('TICKER_OVERLAP',len(set(a.ticker)&set(b.ticker)))
