import pandas as pd,numpy as np,json
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');base=r/'dev79_niche_origin_500x1000_20261019';dest=base/'niche0001_signal_study'
f=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet',columns=['date','ticker','close','ga4_return_5__v1','ga4_return_20__v1','ga4_natr_20__v1','ga4_relative_strength_change_20__v1','ga4_breadth_positive_20__v1'])
f['date']=pd.to_datetime(f.date);f=f.sort_values(['ticker','date']).set_index(['ticker','date'])
samples=[]
for cohort in ['bottom','middle','top']:
 t=pd.read_json(base/'niche0001_trade_replay'/f'{cohort}_shadow_trades.jsonl',lines=True)
 t=t[t.sessions>=5].copy();t['entry_date']=pd.to_datetime(t.entry_date);t['exit_date']=pd.to_datetime(t.exit_date)
 t=t.sample(n=min(5000,len(t)),random_state=17)
 for row in t.itertuples(index=False):
  try: x=f.loc[row.ticker].loc[row.entry_date:row.exit_date]
  except KeyError:continue
  if len(x)<4:continue
  y=x.iloc[2:-1:3]
  for date,z in y.iterrows():
   ahead=x.loc[date:].close.iloc[:6]
   if len(ahead)<3:continue
   entryprice=float(z.close)
   future_loss=float(ahead.min()/entryprice-1)
   samples.append({'cohort':cohort,'ticker':row.ticker,'date':date,'trade_return':row.net_return,'trade_winner':row.net_return>0,'future_adverse5':future_loss<=-.05,'future_min5':future_loss,'ret5':z['ga4_return_5__v1'],'ret20':z['ga4_return_20__v1'],'vol':z['ga4_natr_20__v1'],'rs':z['ga4_relative_strength_change_20__v1'],'breadth':z['ga4_breadth_positive_20__v1']})
df=pd.DataFrame(samples).dropna();df.to_parquet(dest/'intratrade_time_t_samples.parquet',index=False)
report={'observations':len(df),'unique_tickers':df.ticker.nunique(),'future_adverse5_rate':float(df.future_adverse5.mean()),'cohorts':{},'signals':{}}
for k,g in df.groupby('cohort'):report['cohorts'][k]={'observations':len(g),'future_adverse5_rate':float(g.future_adverse5.mean()),'winner_fraction':float(g.trade_winner.mean())}
for feature in ['ret5','ret20','vol','rs','breadth']:
 q=df[feature].quantile([.2,.8]);low=df[df[feature]<=q.iloc[0]];high=df[df[feature]>=q.iloc[1]]
 report['signals'][feature]={'low_adverse_rate':float(low.future_adverse5.mean()),'high_adverse_rate':float(high.future_adverse5.mean()),'low_n':len(low),'high_n':len(high)}
(dest/'intratrade_time_t_screen.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2),flush=True)
