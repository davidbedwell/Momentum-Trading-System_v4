import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');base=r/'dev79_niche_origin_500x1000_20261019';dest=base/'niche0001_signal_study'
f=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet',columns=['date','ticker','open','close','ga4_natr_20__v1'])
f['date']=pd.to_datetime(f.date);f=f.sort_values(['ticker','date'])
f['next_open']=f.groupby('ticker').open.shift(-1)
f['next_date']=f.groupby('ticker').date.shift(-1)
f=f.set_index(['ticker','date'])
threshold=.030044
result=[]
for cohort in ('bottom','middle','top'):
 t=pd.read_json(base/'niche0001_trade_replay'/f'{cohort}_shadow_trades.jsonl',lines=True)
 t=t[t.sessions>=5].copy()
 t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date)
 t=t.sample(n=min(1000,len(t)),random_state=37)
 for trade in t.itertuples(index=False):
  try:x=f.loc[trade.ticker].loc[trade.entry_date:trade.exit_date]
  except KeyError:continue
  if len(x)<3:continue
  signal=x[(x['ga4_natr_20__v1']>=threshold)&(x.index>trade.entry_date)]
  if signal.empty:continue
  sig=signal.iloc[0]
  if pd.isna(sig.next_open) or sig.next_date>trade.exit_date:continue
  original=float(trade.net_return)
  # Proxy: replace original exit with next-session open exit, retaining entry price and same round-trip fee assumption.
  early=(float(sig.next_open)/float(trade.entry)-1)-.002
  result.append({'cohort':cohort,'ticker':trade.ticker,'entry_date':trade.entry_date,'exit_date':trade.exit_date,'signal_date':signal.index[0],'early_exit_date':sig.next_date,'original_return':original,'early_return':early,'delta':early-original,'original_winner':original>0,'early_better':early>original})
df=pd.DataFrame(result);df.to_parquet(dest/'volatility_exit_trade_proxy.parquet',index=False)
summary={'threshold':threshold,'execution':'next available open','caveat':'shadow trades, conditional triggered sample, no portfolio/cash/reentry simulation','triggered_trades':len(df),'cohorts':{}}
for k,g in df.groupby('cohort'):summary['cohorts'][k]={'trades':len(g),'mean_original':float(g.original_return.mean()),'mean_early':float(g.early_return.mean()),'mean_delta':float(g.delta.mean()),'improved_fraction':float(g.early_better.mean()),'winners_interrupted':int(g.original_winner.sum())}
(dest/'volatility_exit_trade_proxy.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
