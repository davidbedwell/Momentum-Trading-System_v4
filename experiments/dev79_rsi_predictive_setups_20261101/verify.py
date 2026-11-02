from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd
p=Path(__file__).resolve().parent
x=pd.read_csv(p/'input_features_with_derivations.csv',parse_dates=['execution_date','exit_date','feature_date']);f=pd.read_csv(p/'setup_flags.csv');r=pd.read_csv(p/'rule_definitions.csv');m=pd.read_csv(p/'setup_monthly_metrics.csv',parse_dates=['execution_date']);cal=pd.read_csv(p/'calibration_2014.csv');sched=pd.read_csv(p/'selection_schedule.csv');member=pd.read_csv(p/'policy_membership.csv',parse_dates=['execution_date']);paths=pd.read_csv(p/'strategy_monthly_returns.csv',parse_dates=['execution_date']);summary=pd.read_csv(p/'oos_classification_metrics.csv');perf=pd.read_csv(p/'strategy_metrics.csv')
assert np.allclose(x.prior15_volume_ratio_60,(20*x.volume_ratio_20_60-5*x.volume_ratio_5_60)/15,equal_nan=True)
for row in cal.itertuples():
 z=m[(m.rule_id==row.rule_id)&(m.execution_date<pd.Timestamp('2013-12-01'))];assert len(z)==59
 assert np.isclose(z.precision_excess.mean(),row.mean_monthly_precision_excess,equal_nan=True)
 assert z.selected_labeled_n.sum()==row.selected_labeled_n
 assert row.eligible==((row.selected_labeled_n>=40)&(row.active_months>=24))
for y in range(2014,2019):
 t=pd.read_csv(p/f'calibration_{y}.csv')
 for s in sched[sched.evaluation_year==y].itertuples():
  family=s.policy.removeprefix('expanding_');q=t[t.eligible]
  if family!='all':q=q[q.family==family]
  q=q.sort_values(['mean_monthly_precision_excess','enrichment','rule_id'],ascending=[False,False,True]);assert s.rule_id==q.iloc[0].rule_id
  assert pd.Timestamp(s.max_train_exit)<pd.Timestamp(y,1,1)
for name,g in member.groupby('strategy'):
 q=summary[summary.strategy==name].iloc[0];s=g[g.selected];assert len(s)==q.selected_labeled_n;assert s.winner.sum()==q.selected_winner_n
 # Independently track dollar holdings and cash through every open.
 value=1.;holdings={};rets=[];trades=[]
 z=paths[paths.strategy==name].sort_values('execution_date')
 for i,(d,a) in enumerate(g.groupby('execution_date',sort=True)):
  selected=a[a.selected];old=value;target={t:old/len(selected) for t in selected.ticker} if len(selected) else {}
  traded=sum(abs(target.get(t,0)-holdings.get(t,0)) for t in set(target)|set(holdings));turn=traded/old;fee=.001*traded
  scale=(old-fee)/old
  holdings={t:dollars*scale*(1+float(selected.loc[selected.ticker.eq(t),'return'].iloc[0])) for t,dollars in target.items()}
  value=sum(holdings.values()) if holdings else old-fee
  if i==58:
   turn+=sum(holdings.values())/value;value-=.001*sum(holdings.values())
  ret=value/old-1;rets.append(ret);trades.append(turn)
 assert np.allclose(rets,z.net_return,atol=1e-12)
 assert np.allclose(trades,z.two_sided_turnover,atol=1e-12)
 expected=value**(12/59)-1;assert np.isclose(expected,perf[perf.strategy.eq(name)].iloc[0].cagr)
# Reproduce every fixed setup's OOS hits and exclusions directly from flags.
oos=x.execution_date.between('2014-01-01','2018-11-30')
for rid in r.rule_id:
 a=summary[summary.strategy.eq(rid)].iloc[0];sel=f[rid]&oos
 assert sel.sum()==a.selected_labeled_n and x.loc[sel,'winner'].sum()==a.selected_winner_n
 assert ((~f[rid])&oos).sum()==a.unselected_labeled_n
assert len(paths.strategy.unique())==len(perf)
audit=json.loads((p/'audit.json').read_text());assert audit['source_sha256']==hashlib.sha256((p.parent/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv').read_bytes()).hexdigest()
print('PASS: independent dollar-accounting replay of all policy/complement returns and turnover; all fixed OOS counts; discovery scores and annual choices; source hash')
# Reviewable monthly policy classifications (including inactive months).
rows=[]
for (name,d),g in member.groupby(['strategy','execution_date']):
 s=g[g.selected];u=g[~g.selected];a=int(s.winner.sum());n=len(s);w=int(g.winner.sum());N=len(g)
 rows.append(dict(strategy=name,execution_date=d,candidate_n=N,winner_n=w,selected_n=n,selected_winner_n=a,unselected_n=len(u),unselected_winner_n=w-a,precision=a/n if n else np.nan,recall=a/w if w else np.nan,enrichment=(a/n)/(w/N) if n else np.nan,selected_mean_return=s['return'].mean(),unselected_mean_return=u['return'].mean(),basket_mean_return=g['return'].mean()))
pd.DataFrame(rows).to_csv(p/'policy_monthly_metrics.csv',index=False)
v=json.loads((p/'verification.json').read_text());v['independent_replay']='PASS: dollar holdings, cash, fees, monthly turnover, net CAGR; training scores/choices and OOS counts';(p/'verification.json').write_text(json.dumps(v,indent=2))
