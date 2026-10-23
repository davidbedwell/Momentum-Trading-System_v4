"""Exploratory pre-entry extension x volatility test; no trading logic changed."""
import json,pathlib
import numpy as np,pandas as pd
P=pathlib.Path('/opt/mts/ga6/runs/post_v3_comparison_20261022');D=pathlib.Path('/opt/mts/thunder-migration/mts-certification-20261011/dev87')
t=pd.read_csv(P/'dev87_trade_level_drawdown_features.csv');t['entry_date']=pd.to_datetime(t.entry_date)
f=pd.read_parquet(D/'dev87_ga6_enriched.parquet');f['date']=pd.to_datetime(f.date);f=f.sort_values(['ticker','date']);f['next_date']=f.groupby('ticker').date.shift(-1)
features=['ga4_return_126__v1','ga4_return_252__v1','ga4_return_63__v1','ga4_close_to_sma_200__v1','ga4_close_to_sma_50__v1','ga4_natr_14__v1','ga4_natr_20__v1','ga4_realized_vol_20__v1','ga4_realized_vol_63__v1','ga4_return_252_percentile__v1','ga4_natr_20_percentile__v1','trend','breadth','relative_strength']
assert set(features).issubset(f.columns)
d=t.merge(f[['ticker','next_date',*features]],left_on=['ticker','entry_date'],right_on=['ticker','next_date'],how='left',validate='many_to_one');assert d.ga4_return_126__v1.notna().mean()>.95
# Primary preregistered-in-code operational definitions, fixed economic cutoffs.
# Extended = 126d return >=30% AND close >=10% above SMA200.
# Volatile = NATR14 >=4% (14-session average true range / close).
d['extended']=(d.ga4_return_126__v1>=.30)&(d.ga4_close_to_sma_200__v1>=.10)
d['volatile']=(d.ga4_natr_14__v1>=.04)
d['extended_volatile']=d.extended&d.volatile
d['win']=d.trade_return>0;d['loss']=d.trade_return<0;d['flat']=d.trade_return==0;d['severe_loss']=d.trade_return<=-.10;d['high_mae']=d.mae<=-.10
d['entry_group']=np.select([d.extended_volatile,d.extended&~d.volatile,~d.extended&d.volatile],['extended+volatile','extended only','volatile only'],default='neither')
# Niche labels are associated with chromosomes, not necessarily the traded stock's niche.
sel=pd.read_csv(P/'dev87_53_survivors_ranked.csv')[['definition_hash','niche']].rename(columns={'definition_hash':'chromosome'});d=d.merge(sel,on='chromosome',validate='many_to_one')
def metrics(x):
 n=len(x)
 if not n:return {'n':0}
 w=int(x.win.sum());l=int(x.loss.sum());p=w/n;z=1.96;center=(p+z*z/(2*n))/(1+z*z/n);radius=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
 return {'n':n,'wins':w,'losses':l,'flat':int(x.flat.sum()),'win_pct':100*p,'loss_pct':100*l/n,'win_rate_wilson95_pct':[100*(center-radius),100*(center+radius)],'avg_win_pct':100*x.loc[x.win,'trade_return'].mean(),'avg_loss_pct':100*x.loc[x.loss,'trade_return'].mean(),'median_win_pct':100*x.loc[x.win,'trade_return'].median(),'median_loss_pct':100*x.loc[x.loss,'trade_return'].median(),'mean_trade_return_pct':100*x.trade_return.mean(),'median_trade_return_pct':100*x.trade_return.median(),'severe_loss_pct':100*x.severe_loss.mean(),'adverse_excursion_10pct':100*x.high_mae.mean(),'median_mae_pct':100*x.mae.median(),'median_mfe_pct':100*x.mfe.median(),'median_hold_sessions':float(x.sessions.median()),'avg_hold_sessions':float(x.sessions.mean()),'median_126d_prior_return_pct':100*x.ga4_return_126__v1.median(),'median_entry_natr14_pct':100*x.ga4_natr_14__v1.median()}
report={'status':'EXPLORATORY','definitions':{'extended':'Prior-session 126-day return >=30% AND close >=10% above 200-day moving average','volatile':'Prior-session normalized ATR14 >=4%','primary':'extended AND volatile','gain_loss':'Completed-position net realized P&L, including fills and fees, divided by total buy notional','universe':'53 selected Structural v3 chromosomes on DEV87; Jan 2025–Sep 2026'},'groups':{g:metrics(x) for g,x in d.groupby('entry_group')},'primary_vs_rest':{'primary':metrics(d[d.extended_volatile]),'rest':metrics(d[~d.extended_volatile])},'by_niche':{n:{'primary':metrics(x[x.extended_volatile]),'rest':metrics(x[~x.extended_volatile])} for n,x in d.groupby('niche')},'sensitivity':{},'unique_ticker_entry':{},'limitations':['Retrospective threshold study on already-selected DEV87 chromosomes; selection bias and multiple testing remain','Repeated chromosome entries are correlated; Wilson intervals assume independent observations and understate uncertainty','Entry indicators taken from preceding available stock session, not execution-day future information','P&L percentage based on executed cash fills; open positions excluded','MAE excludes entry-day intraday low to avoid pre-entry lookahead','No evidence of causality or portfolio-level impact without a fresh holdout and full replay']}
# Single-factor and joint threshold sensitivity, not optimized to a desired outcome.
for advance in (.20,.30,.40,.50):
 for atr in (.03,.04,.05,.06):
  flag=(d.ga4_return_126__v1>=advance)&(d.ga4_close_to_sma_200__v1>=.10)&(d.ga4_natr_14__v1>=atr)
  report['sensitivity'][f'ret126>={advance:.0%};sma200>=10%;natr14>={atr:.0%}']={'flagged':metrics(d[flag]),'other':metrics(d[~flag])}
# Distinct ticker-entry pairs: collapse repeated chromosomes, report both equal-event and chromosome-weighted views.
u=d.groupby(['ticker','entry_date'],as_index=False).agg(trade_return=('trade_return','mean'),win=('win','mean'),loss=('loss','mean'),severe_loss=('severe_loss','mean'),high_mae=('high_mae','mean'),extended_volatile=('extended_volatile','first'),chromosome_entries=('chromosome','nunique'))
for label,x in [('primary',u[u.extended_volatile]),('rest',u[~u.extended_volatile])]:
 report['unique_ticker_entry'][label]={'unique_events':len(x),'mean_fraction_winning_chromosomes_pct':100*x.win.mean(),'mean_fraction_losing_chromosomes_pct':100*x.loss.mean(),'mean_fraction_severe_loss_pct':100*x.severe_loss.mean(),'mean_return_across_chromosomes_pct':100*x.trade_return.mean(),'median_chromosomes_per_event':float(x.chromosome_entries.median())}
# Concentration diagnostics.
report['concentration']={'distinct_chromosomes_primary':int(d.loc[d.extended_volatile,'chromosome'].nunique()),'distinct_tickers_primary':int(d.loc[d.extended_volatile,'ticker'].nunique()),'primary_trades':int(d.extended_volatile.sum()),'unique_ticker_entry_events':len(u),'all_trades':len(d)}
d[['chromosome','niche','ticker','entry_date','exit_date','sessions','trade_return','mae','mfe','ga4_return_126__v1','ga4_close_to_sma_200__v1','ga4_natr_14__v1','extended','volatile','extended_volatile','entry_group','win','loss','severe_loss']].to_csv(P/'dev87_entry_extension_volatility_trade_classification.csv',index=False)
(P/'dev87_entry_extension_volatility_study.json').write_text(json.dumps(report,indent=2,allow_nan=False));print(json.dumps({k:report[k] for k in ['definitions','groups','primary_vs_rest','unique_ticker_entry','concentration']},indent=2,allow_nan=False))
