import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import pandas as pd,numpy as np,json,itertools,hashlib
P=Path(__file__).resolve().parent;E=P.parent
r=pd.read_csv(P/'full_ranked.csv');m=pd.read_csv(P/'monthly.csv',parse_dates=['execution_date','end_date']);s=pd.read_csv(P/'selections.csv',parse_dates=['execution_date']);f=pd.read_csv(P/'candidate_flags.csv',parse_dates=['execution_date','feature_date']);panel=pd.read_csv(P/'panel.csv');a=json.loads((P/'audit.json').read_text())
assert {int(k):int(v) for k,v in r.groupby('order').size().items()}=={0:1,1:9,2:36,3:84}
assert len(m)==120*130*2 and m.groupby(['strategy','kind']).size().eq(120).all()
assert f.feature_date.lt(f.execution_date).all();assert a['plan_sha256']==hashlib.sha256((P/'PLAN.md').read_bytes()).hexdigest()
h=pd.read_csv(E/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/holdings.csv',parse_dates=['execution_date'])
assert set(zip(h.execution_date,h.ticker))==set(zip(f.execution_date,f.ticker))
x=pd.read_csv(E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv');x['vol_ratio_10_21']=x.vol_10/x.vol_21
for row in panel.itertuples():
 yes=np.isfinite(x[row.feature])&((x[row.feature]>row.threshold) if row.direction=='>' else (x[row.feature]<row.threshold));assert np.array_equal(yes,f[row.feature])
for row in r.itertuples():
 ids=[] if row.strategy=='control' else [int(i)-1 for i in row.strategy.split('_')[1].split('-')]
 yes=np.ones(len(f),dtype=bool) if not ids else f[[panel.feature.iloc[i] for i in ids]].all(axis=1)
 assert set(zip(f.loc[yes,'execution_date'],f.loc[yes,'ticker']))==set(zip(s.loc[s.strategy.eq(row.strategy),'execution_date'],s.loc[s.strategy.eq(row.strategy),'ticker']))
# Independent holdings-dollar ledger; solve commission with bisection, not source iteration.
d=pd.read_parquet('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet',filters=[('date','<',pd.Timestamp('2019-01-01'))]);d.date=pd.to_datetime(d.date);d['ao']=d.open*d.adj_close/d.close
# Rebuild RSI and original prior-close eligibility independently from truncated prices.
c=d.pivot(index='date',columns='ticker',values='adj_close').sort_index();delta=c.diff();gain=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean();loss=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean();rsi=100-100/(1+gain/loss)
for date,g in f.groupby('execution_date'):
 prior=c.index[c.index.get_loc(date)-1];valid=np.isfinite(c.loc[prior])&(c.loc[prior]>0)&np.isfinite(rsi.loc[prior]);ids=np.flatnonzero(valid);chosen=ids[np.argsort(rsi.loc[prior].to_numpy()[ids],kind='stable')[:max(1,len(ids)//5)]];assert set(c.columns[chosen])==set(g.ticker)
prices=d.set_index(['date','ticker']);open_prices=prices.ao.to_dict();close_prices=prices.adj_close.to_dict();maxerr=0
by={k:g for k,g in s.groupby(['strategy','execution_date'])};base={k:g for k,g in s[s.strategy.eq('control')].groupby('execution_date')}
for (rid,kind),g in m.groupby(['strategy','kind']):
 prev={};nav=1.
 for row in g.sort_values('execution_date').itertuples():
  chosen=by.get((rid,row.execution_date));names=[] if chosen is None else list(chosen.ticker)
  if kind=='matched_control' and names:names=list(base[row.execution_date].ticker)
  n=len(names);target={t:1/n for t in names};keys=set(prev)|set(target)
  low,high=0.,.01
  for _ in range(50):
   fee=(low+high)/2;rhs=.001*sum(abs((1-fee)*target.get(t,0)-prev.get(t,0)) for t in keys)
   if fee>rhs:high=fee
   else:low=fee
  fee=(low+high)/2
  end={t:(1-fee)/n*(close_prices if row.terminal_close else open_prices)[(row.end_date,t)]/open_prices[(row.execution_date,t)] for t in names}
  wealth=sum(end.values()) if n else (1-fee)
  err=abs(wealth-1-row.net_return);maxerr=max(maxerr,err);assert err<1e-11
  nav*=wealth;assert abs(nav-row.nav)<1e-9
  prev={t:v/wealth for t,v in end.items()}
  assert row.count==n
 g1=g.sort_values('execution_date');w=np.prod(1+g1.net_return);rank=r[r.strategy.eq(rid)].iloc[0];key='cagr' if kind=='selected' else 'matched_cagr';assert abs(w**(252/a['sessions'])-1-rank[key])<1e-10
for rid,g in m.groupby('strategy'):
 selected=g[g.kind.eq('selected')].sort_values('execution_date');matched=g[g.kind.eq('matched_control')].sort_values('execution_date');np.testing.assert_allclose(selected.exposure,matched.exposure,atol=1e-14)
orig=pd.read_csv(E/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/monthly.csv');control=m[m.strategy.eq('control')&m.kind.eq('selected')];np.testing.assert_allclose(control.net_return,orig.strategy_return,atol=1e-12)
assert len(pd.read_csv(P/'annual.csv'))==2600;assert len(pd.read_csv(P/'year_slices.csv'))==1040
v=dict(status='PASS',exhaustive_counts=True,monthly_dollar_ledger_max_error=maxerr,exact_memberships=True,exact_original_control=True,identical_matched_exposure=True,no_2019_rows=True)
(P/'verification.json').write_text(json.dumps(v,indent=2));print(json.dumps(v,indent=2))
