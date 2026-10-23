import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');base=r/'dev79_niche_origin_500x1000_20261019';dest=base/'niche0001_signal_study'
f=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet',columns=['date','ticker','open','close','ga4_natr_20__v1','ga4_relative_strength_change_20__v1'])
f.date=pd.to_datetime(f.date);f=f.sort_values(['ticker','date'])
g=f.groupby('ticker',sort=False)
f['sma10']=g.close.transform(lambda x:x.rolling(10,min_periods=10).mean())
f['sma10_prior']=g.sma10.shift(3) if 'sma10' in g.obj.columns else f.groupby('ticker').sma10.shift(3)
f['ret5']=g.close.pct_change(5)
f['next_open']=g.open.shift(-1);f['next_date']=g.date.shift(-1)
f=f.set_index(['ticker','date'])
threshold=.030044
policies={
 'vol_only':lambda x:(x['ga4_natr_20__v1']>=threshold),
 'vol_and_below_sma10':lambda x:(x['ga4_natr_20__v1']>=threshold)&(x.close<x.sma10),
 'vol_and_falling_sma10':lambda x:(x['ga4_natr_20__v1']>=threshold)&(x.sma10<x.sma10_prior),
 'vol_and_negative_5day':lambda x:(x['ga4_natr_20__v1']>=threshold)&(x.ret5<0),
 'vol_and_below_sma10_and_falling':lambda x:(x['ga4_natr_20__v1']>=threshold)&(x.close<x.sma10)&(x.sma10<x.sma10_prior),
 'vol_and_negative_rs':lambda x:(x['ga4_natr_20__v1']>=threshold)&(x['ga4_relative_strength_change_20__v1']<0)
}
rows=[]
for cohort in ('bottom','middle','top'):
 t=pd.read_json(base/'niche0001_trade_replay'/f'{cohort}_shadow_trades.jsonl',lines=True)
 t=t[t.sessions>=5].copy();t.entry_date=pd.to_datetime(t.entry_date);t.exit_date=pd.to_datetime(t.exit_date)
 t=t.sample(n=min(1000,len(t)),random_state=37)
 for trade in t.itertuples(index=False):
  try:x=f.loc[trade.ticker].loc[trade.entry_date:trade.exit_date]
  except KeyError:continue
  if len(x)<3:continue
  original=float(trade.net_return)
  for name,fn in policies.items():
   signal=x[fn(x)&(x.index>trade.entry_date)]
   if signal.empty:early=original;trigger=False
   else:
    z=signal.iloc[0]
    if pd.isna(z.next_open) or z.next_date>trade.exit_date:early=original;trigger=False
    else:early=float(z.next_open)/float(trade.entry)-1-.002;trigger=True
   rows.append({'cohort':cohort,'policy':name,'original':original,'modified':early,'delta':early-original,'trigger':trigger,'original_winner':original>0})
df=pd.DataFrame(rows);df.to_parquet(dest/'directional_volatility_trade_proxy.parquet',index=False)
summary=[]
for (cohort,policy),g in df.groupby(['cohort','policy']):
 triggered=g[g.trigger]
 summary.append({'cohort':cohort,'policy':policy,'trades':len(g),'triggered':len(triggered),'trigger_rate':g.trigger.mean(),'mean_original_all':g.original.mean(),'mean_modified_all':g.modified.mean(),'mean_delta_all':g.delta.mean(),'mean_delta_triggered':triggered.delta.mean() if len(triggered) else None,'improved_triggered':(triggered.delta>0).mean() if len(triggered) else None})
pd.DataFrame(summary).to_csv(dest/'directional_volatility_policy_comparison.csv',index=False)
print(pd.DataFrame(summary).to_string(index=False),flush=True)
