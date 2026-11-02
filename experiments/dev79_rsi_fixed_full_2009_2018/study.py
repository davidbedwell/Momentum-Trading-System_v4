from pathlib import Path
import hashlib,json,time
import numpy as np
import pandas as pd
P=Path(__file__).resolve().parent
S=P.parent/'dev79_rsi_predictive_setups_20261101'
start=time.monotonic()
x=pd.read_csv(S/'input_features_with_derivations.csv',parse_dates=['execution_date','feature_date','exit_date'])
r=pd.read_csv(S/'discovery_ranked_setups.csv')
q=r[r.eligible].sort_values(['mean_monthly_precision_excess','enrichment','rule_id'],ascending=[False,False,True])
assert q.iloc[0].rule_id=='stabilization_09' and q.iloc[0].discovery_rank==1
assert q.iloc[0].definition=='ma_distance_20 < 0 AND acceleration_21 > 0'
assert pd.Timestamp(q.iloc[0].max_train_exit)<pd.Timestamp('2014-01-01')
mask=x.ma_distance_20.lt(0)&x.acceleration_21.gt(0)&np.isfinite(x[['ma_distance_20','acceleration_21']]).all(axis=1)
flags=pd.read_csv(S/'setup_flags.csv');assert np.array_equal(mask,flags.stabilization_09)
old=pd.read_csv(S/'policy_membership.csv',parse_dates=['execution_date']);old=old[old.strategy.eq('frozen_all')]
check=x[['execution_date','ticker']].assign(selected=mask).merge(old[['execution_date','ticker','selected']],on=['execution_date','ticker'],suffixes=('_new','_old'),validate='one_to_one')
assert len(check)==len(old) and check.selected_new.eq(check.selected_old).all()
assert x.execution_date.dt.to_period('M').nunique()==120
assert x.execution_date.dt.year.between(2009,2018).all() and x.feature_date.lt(x.execution_date).all()
assert x.exit_date.dropna().dt.year.le(2018).all()
assert x.loc[x.execution_date.lt('2018-12-01'),'return'].notna().all()
assert x.loc[x.execution_date.ge('2018-12-01'),'return'].isna().all()
assert np.allclose(x['return'],x.exit_open/x.entry_open-1,equal_nan=True)
x['sample_label']=np.where(x.execution_date.dt.year.le(2013),'in-sample retrospective','previously examined OOS; no new validation')
x['frozen_all_selected']=mask
x.to_csv(P/'candidate_membership.csv',index=False)
rows=[];ledger=[];metrics=[];annual=[]
def perf(g):
 if g.net_return.isna().any():return dict(net_cagr=np.nan,mdd_monthly=np.nan,sharpe=np.nan,status='UNAVAILABLE: December 2018 exit requires prohibited 2019 data')
 a=g.net_return.to_numpy();w=np.r_[1,np.cumprod(1+a)]
 return dict(net_cagr=w[-1]**(12/len(a))-1,mdd_monthly=min(w/np.maximum.accumulate(w)-1),sharpe=np.mean(a)/np.std(a,ddof=1)*np.sqrt(12),status='observed continuous segment; no terminal liquidation')
for name,m in [('frozen_all',mask),('baseline_rsi_lowest20pct',pd.Series(True,index=x.index))]:
 prev={};nav=1.;dollars={}
 for date,g in x.groupby('execution_date',sort=True):
  chosen=g[m.loc[g.index]];n=len(chosen);target={t:1/n for t in chosen.ticker} if n else {}
  tickers=sorted(set(prev)|set(target));buy=sum(max(target.get(t,0)-prev.get(t,0),0) for t in tickers);sell=sum(max(prev.get(t,0)-target.get(t,0),0) for t in tickers);cost=.001*(buy+sell)
  observed=chosen['return'].notna().all();gross=chosen['return'].sum()/n if n and observed else 0. if not n else np.nan
  net=(1-cost)*(1+gross)-1
  # Independent dollar holdings and cash replay.
  traded=sum(abs(nav*target.get(t,0)-dollars.get(t,0)) for t in tickers)
  assert np.isclose(traded/nav,buy+sell,atol=1e-12)
  ending={t:nav*(1-cost)*w*(1+float(chosen.loc[chosen.ticker.eq(t),'return'].iloc[0])) for t,w in target.items()} if observed else {}
  endnav=sum(ending.values()) if n and observed else nav*(1-cost) if not n else np.nan
  if observed:assert np.isclose(endnav/nav-1,net,atol=1e-12)
  for t in tickers:
   z=chosen[chosen.ticker.eq(t)];rr=z['return'].iloc[0] if len(z) else np.nan
   ledger.append(dict(strategy=name,execution_date=date,ticker=t,prior_drift_weight=prev.get(t,0),target_weight=target.get(t,0),buy_weight=max(target.get(t,0)-prev.get(t,0),0),sell_weight=max(prev.get(t,0)-target.get(t,0),0),trade_fee_fraction=.001*abs(target.get(t,0)-prev.get(t,0)),stock_return=rr,gross_return_contribution=target.get(t,0)*rr if len(z) else 0.,net_nav_return_contribution=(1-cost)*target.get(t,0)*rr if len(z) else 0.))
  rows.append(dict(strategy=name,execution_date=date,exit_date=g.exit_date.max(),sample_label=g.sample_label.iloc[0],rule_id='stabilization_09' if name=='frozen_all' else 'baseline',holdings_n=n,selected_stocks=';'.join(sorted(chosen.ticker)),buy_turnover=buy,sell_turnover=sell,transaction_cost_fraction=cost,gross_return=gross,net_return=net,nav_start=nav,nav_end=endnav,missing_return_n=int(chosen['return'].isna().sum()),status='observed' if observed else 'MISSING: next-month exit in 2019 prohibited'))
  if observed:
   prev={t:w*(1+float(chosen.loc[chosen.ticker.eq(t),'return'].iloc[0]))/(1+gross) for t,w in target.items()};nav=endnav;dollars=ending
 z=pd.DataFrame(rows);z=z[z.strategy.eq(name)]
 metrics.append(dict(strategy=name,months=120,years=10,active_months=int(z.holdings_n.gt(0).sum()),selected_stock_months=int(z.holdings_n.sum()),observed_return_months=int(z.net_return.notna().sum()),**perf(z)))
 for year,g in z.groupby(z.execution_date.dt.year):annual.append(dict(strategy=name,year=year,sample_label=g.sample_label.iloc[0],months=len(g),active_months=int(g.holdings_n.gt(0).sum()),**perf(g)))
monthly=pd.DataFrame(rows);ledger=pd.DataFrame(ledger)
for (name,date),g in ledger.groupby(['strategy','execution_date']):
 z=monthly[(monthly.strategy==name)&(monthly.execution_date==date)].iloc[0]
 assert np.isclose(g.trade_fee_fraction.sum(),z.transaction_cost_fraction)
 if pd.notna(z.net_return):assert np.isclose(g.net_nav_return_contribution.sum()-z.transaction_cost_fraction,z.net_return)
monthly.to_csv(P/'monthly_return_reconciliation.csv',index=False);ledger.to_csv(P/'stock_return_reconciliation.csv',index=False)
pd.DataFrame(metrics).to_csv(P/'full_period_metrics.csv',index=False);pd.DataFrame(annual).to_csv(P/'annual_metrics.csv',index=False)
x[mask].to_csv(P/'selected_stocks.csv',index=False)
provenance={'rule_id':'stabilization_09','definition':q.iloc[0].definition,'discovery':q.iloc[0].to_dict(),'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'study.py',S/'discovery_ranked_setups.csv',S/'policy_membership.csv',S/'input_features_with_derivations.csv']},'seconds':time.monotonic()-start,'rule_verification':'PASS: unique discovery winner, saved flags and all saved frozen_all OOS memberships match','accounting_verification':'PASS: independent dollar replay and stock contribution reconciliation','full_period_status':'BLOCKED: original December 2018 holding exits in January 2019; no data fetched or loaded','terminal_liquidation':'not applied: authorized terminal exit unavailable; no substitute exit or zero-return proxy','cost':'0.001 per bought/sold notional; net=(1-cost)*(1+gross)-1; drift adjusted rebalance','raw_data_loaded':False,'learning_or_optimization':False}
(P/'audit.json').write_text(json.dumps(provenance,indent=2,default=str))
lines=['# Fixed RSI full retrospective: endpoint blocked','','Frozen rule uniquely established from the saved 2009–2013 discovery ranking: `stabilization_09`, RSI lowest20% basket AND `ma_distance_20 < 0` AND `acceleration_21 > 0`. Original discovery cutoff 2014-01-01; last discovery entry 2013-11-01 and exit 2013-12-02. No new ranking, calibration, warmup phase, fallback or optimization. Existing pre-entry features used unchanged.','','Applied unchanged to all 120 entry months, January 2009–December 2018. 2009–2013 is **in-sample retrospective**; 2014–2018 is **previously examined OOS**, with **no new validation claim**.','','Full-period net CAGR, monthly MDD and Sharpe are **unavailable**. Original next-month-first-session adjusted-open accounting requires January 2019 data to value December 2018. Those data are prohibited. Neither a zero return, omitted month, nor a December liquidation is substituted. Final liquidation and December NAV cannot be reconciled. All 120 monthly decisions are exported; 119 returns are observed. The supplied history carries fixed-universe/survivorship and vendor price-adjustment limitations.','','|Strategy|Years / months|Active months|Selected stock-months|Net CAGR|Monthly MDD|Sharpe|','|---|---:|---:|---:|---:|---:|---:|']
for a in metrics:lines.append(f"|{a['strategy']}|10 / 120|{a['active_months']}|{a['selected_stock_months']}|unavailable|unavailable|unavailable|")
lines+=['','Costs and observed accounting match the prior study: 10bps per buy/sell notional, equal monthly weights, drift-adjusted turnover, zero-return cash for empty selections. Initial purchase charged. Monthly net = (1-cost) × (1+gross) − 1. No terminal fee fabricated. Sharpe convention: monthly mean/sample SD × sqrt(12), zero risk-free rate; CAGR annualizes at 12/months and MDD includes initial NAV. Annual observed segments continue the same portfolio without annual restarts; 2018 metrics are unavailable.','','Artifacts: `selected_stocks.csv`, `candidate_membership.csv`, `monthly_return_reconciliation.csv` (120 rows per strategy, stock lists, NAV, fees and missing terminal return), `stock_return_reconciliation.csv` (drift/target weights, trades, fees and return contributions), `annual_metrics.csv`, `full_period_metrics.csv`, `audit.json`. Independent dollar-accounting replay, exact stored rule flags and prior frozen_all memberships all PASS. No production files, GA, raw data or 2019+ observations used. Reproduce with `bash experiments/dev79_rsi_fixed_full_2009_2018/run.sh` (900-second timeout).']
(P/'REPORT.md').write_text('\n'.join(lines)+'\n')
print(pd.DataFrame(metrics).to_string(index=False));print('PASS decisions/reconciliation; BLOCKED full-period terminal metrics')
