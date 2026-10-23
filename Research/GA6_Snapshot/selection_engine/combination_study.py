"""Frozen chromosome agreement study: entry-date consensus vs standalone, with split-adjusted close-to-close proxy outcomes. Research only, NOT an executable portfolio backtest."""
import json
from pathlib import Path
from collections import defaultdict
import pandas as pd,numpy as np
ROOT=Path('/opt/mts');OUT=ROOT/'ga6_h/selection_engine'
cohorts={'DEV79':'ga5_redesign/exploratory79_ga4_enriched.parquet','DEV87':'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet','DEV50b':'ga6_h/dev50b/DEV50b_enriched.parquet'}
# Same-day agreement on symbol and actual entry date. No forward outcomes used for selecting chromosomes.
result=[];detail=[]
for cohort,path in cohorts.items():
 d=pd.read_csv(ROOT/f'ga6_h/audits/GA6v3_400_{cohort}_trade_ledger_2019_2024.csv'); ledger=defaultdict(list)
 for r in d.itertuples():
  if r.status!='OK' or not isinstance(r.trade_ledger,str):continue
  for trade in json.loads(r.trade_ledger):
   if trade.get('exit_date') and trade.get('entry_date'):ledger[(trade['symbol'],trade['entry_date'])].append((int(r.index),trade['exit_date']))
 frame=pd.read_parquet(ROOT/path,columns=['ticker','date','close','open','stock_splits']);frame=frame[(frame.date>='2019-01-01')&(frame.date<'2025-01-01')];frame['date']=frame.date.dt.strftime('%Y-%m-%d')
 prices={(t,dt):float(px) for t,dt,px in frame[['ticker','date','close']].itertuples(index=False,name=None) if pd.notna(px) and px>0}
 # Hold fixed 10 sessions after signal to compare identical outcome horizons; no per-chromosome exit contamination.
 forward={}
 for t,g in frame.sort_values(['ticker','date']).groupby('ticker',sort=False):
  dates=g.date.tolist();px=g.close.to_numpy(dtype=float)
  for j in range(len(g)-10):
   if px[j]>0 and np.isfinite(px[j+10]):forward[(t,dates[j])]=float(px[j+10]/px[j]-1-.002)
 # Consensus counts use unique trade-timing signatures (exact identical full-history behavior is one vote).
 signatures={};unique={}
 for r in d.itertuples():
  try: sig=tuple(sorted((x['symbol'],x['entry_date'],x.get('exit_date')) for x in json.loads(r.trade_ledger)))
  except (ValueError,TypeError):continue
  if sig and sig not in signatures:signatures[sig]=int(r.index)
  if sig:unique[int(r.index)]=signatures[sig]
 for (symbol,dt),votes in ledger.items():
  ret=forward.get((symbol,dt));
  if ret is None:continue
  distinct=sorted(set(unique.get(i,i) for i,_ in votes));count=len(distinct)
  detail.append({'cohort':cohort,'symbol':symbol,'entry_date':dt,'independent_votes':count,'proxy_net_return_10s':ret,'winning':ret>0,'representatives':';'.join(map(str,distinct))})
 detailco=[x for x in detail if x['cohort']==cohort]
 for threshold in [1,2,3,4,5]:
  sample=[x for x in detailco if x['independent_votes']>=threshold]
  result.append({'cohort':cohort,'min_distinct_agreeing_chromosomes':threshold,'distinct_symbol_date_signals':len(sample),'proxy_win_rate':sum(x['winning'] for x in sample)/len(sample) if sample else np.nan,'proxy_mean_net_return_10s':np.mean([x['proxy_net_return_10s'] for x in sample]) if sample else np.nan})
pd.DataFrame(result).to_csv(OUT/'agreement_10session_summary.csv',index=False);pd.DataFrame(detail).to_csv(OUT/'agreement_10session_events.csv',index=False)
print(pd.DataFrame(result).to_string(index=False,float_format=lambda x:f'{x:.4f}'))
