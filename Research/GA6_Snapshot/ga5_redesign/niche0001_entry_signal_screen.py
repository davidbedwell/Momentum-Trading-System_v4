import pandas as pd,numpy as np,json
from pathlib import Path
root=Path(__file__).resolve().parent
out=root/'dev79_niche_origin_500x1000_20261019'
dest=out/'niche0001_signal_study';dest.mkdir(exist_ok=True)
features=['ga4_return_5__v1','ga4_return_20__v1','ga4_close_to_sma_20__v1','ga4_close_to_sma_200__v1','ga4_sma20_slope_5__v1','ga4_natr_20__v1','ga4_realized_vol_20__v1','ga4_relative_strength_change_20__v1','ga4_breadth_positive_20__v1','ga4_breadth_above_sma_200__v1','ga4_failed_breakout_20__v1']
frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet',columns=['date','ticker','close']+features)
frame['date']=pd.to_datetime(frame.date).dt.strftime('%Y-%m-%d')
frame=frame.sort_values(['ticker','date'])
for h in (3,5,10):
 frame[f'fwd_{h}']=frame.groupby('ticker').close.shift(-h)/frame.close-1
frame=frame.set_index(['ticker','date'])
rows=[]
for cohort in ('bottom','middle','top'):
 trades=pd.read_json(out/'niche0001_trade_replay'/f'{cohort}_shadow_trades.jsonl',lines=True)
 trades['entry_date']=pd.to_datetime(trades.entry_date).dt.strftime('%Y-%m-%d')
 trades['exit_date']=pd.to_datetime(trades.exit_date).dt.strftime('%Y-%m-%d')
 for t in trades.itertuples(index=False):
  if t.entry_date not in frame.loc[t.ticker].index if t.ticker in frame.index.get_level_values(0) else True:continue
  x=frame.loc[(t.ticker,t.entry_date)]
  row={'cohort':cohort,'ticker':t.ticker,'entry_date':t.entry_date,'exit_date':t.exit_date,'trade_return':t.net_return,'mae':t.mae,'mfe':t.mfe,'sessions':t.sessions,'loser':int(t.net_return<0),'large_adverse':int(t.mae<=-.10)}
  row.update({k:x[k] for k in features});row.update({f'fwd_{h}':x[f'fwd_{h}'] for h in (3,5,10)})
  rows.append(row)
data=pd.DataFrame(rows)
data.to_parquet(dest/'entry_trade_features.parquet',index=False)
report={'n':len(data),'cohorts':{},'signals':{}}
for cohort,g in data.groupby('cohort'):
 report['cohorts'][cohort]={'trades':len(g),'loser_rate':round(g.loser.mean(),4),'large_adverse_rate':round(g.large_adverse.mean(),4),'median_mae':round(g.mae.median(),4)}
for f in features:
 v=data[[f,'loser','large_adverse','cohort']].replace([np.inf,-np.inf],np.nan).dropna()
 if len(v)<100:continue
 q=v[f].quantile([.2,.8]);low=v[v[f]<=q.iloc[0]];high=v[v[f]>=q.iloc[1]]
 report['signals'][f]={'low_quintile_loss_rate':round(low.loser.mean(),4),'high_quintile_loss_rate':round(high.loser.mean(),4),'low_quintile_adverse_rate':round(low.large_adverse.mean(),4),'high_quintile_adverse_rate':round(high.large_adverse.mean(),4),'n':len(v)}
(dest/'entry_signal_screen.json').write_text(json.dumps(report,indent=2))
print('COMPLETE',dest,'TRADES',len(data),flush=True)
for k,v in report['cohorts'].items():print(k,v,flush=True)
for k,v in report['signals'].items():print(k,v,flush=True)
