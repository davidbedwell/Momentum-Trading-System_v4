import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import pandas as pd,numpy as np,itertools,json,hashlib,importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent; E=P.parent
spec=importlib.util.spec_from_file_location('original',E/'dev79_monthly_indicator_20261101/indicator_experiment.py');orig=importlib.util.module_from_spec(spec);spec.loader.exec_module(orig)
x=pd.read_csv(E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv',parse_dates=['execution_date','feature_date'])
x['vol_ratio_10_21']=x.vol_10/x.vol_21
panel=[('return_252','>',0),('ma_distance_20','<',0),('return_5','>',0),('acceleration_21','>',0),('reversal_5_vs_prior21','>',0),('positive_fraction_21','>',.5),('vol_ratio_10_21','<',1),('volume_ratio_5_20','<',1),('relative_strength_21','>',0)]
pd.DataFrame(panel,columns=['feature','direction','threshold']).to_csv(P/'panel.csv',index=False)
flags=np.array([(np.isfinite(x[f]) & ((x[f]>v) if op=='>' else (x[f]<v))).to_numpy() for f,op,v in panel]).T
pd.concat([x[['execution_date','feature_date','ticker']],pd.DataFrame(flags,columns=[p[0] for p in panel])],axis=1).to_csv(P/'candidate_flags.csv',index=False)
d=pd.read_parquet(orig.SOURCE,filters=[('date','<',pd.Timestamp('2019-01-01'))]);d.date=pd.to_datetime(d.date)
c=d.pivot(index='date',columns='ticker',values='adj_close').sort_index();raw=d.pivot(index='date',columns='ticker',values='close').reindex_like(c);o=d.pivot(index='date',columns='ticker',values='open').reindex_like(c)*c/raw
idx=c.index; dates=sorted(x.execution_date.unique()); starts=[idx.get_loc(t) for t in dates];last=np.flatnonzero(idx<=pd.Timestamp('2018-12-31'))[-1];sessions=last-starts[0]+1
cv=c.to_numpy();ov=o.to_numpy(); col={t:i for i,t in enumerate(c.columns)};groups=[x.index[x.execution_date.eq(t)].to_numpy() for t in dates]
rules=[('control',())]+[(f'k{k}_'+ '-'.join(str(i+1) for i in ids),ids) for k in [1,2,3] for ids in itertools.combinations(range(9),k)]
R=len(rules);N=len(c.columns);targets=np.zeros((120,R,N));membership=[]
for m,g in enumerate(groups):
 for a,(rid,ids) in enumerate(rules):
  chosen=g if not ids else g[flags[g][:,ids].all(axis=1)]
  if len(chosen):targets[m,a,[col[t] for t in x.loc[chosen,'ticker']]]=1/len(chosen)
  for row in chosen:membership.append((rid,str(pd.Timestamp(dates[m]).date()),x.at[row,'ticker']))
pd.DataFrame(membership,columns=['strategy','execution_date','ticker']).to_csv(P/'selections.csv',index=False)
# Matched control for every rule, with exactly identical capital exposure schedule.
T=np.concatenate([targets,np.where(targets.sum(axis=2,keepdims=True)>0,targets[:,0:1,:],0)],axis=1)
prev=np.zeros((2*R,N));nav=np.ones(2*R);daily=[];rows=[]
for m,i in enumerate(starts):
 j=starts[m+1] if m<119 else last;terminal=m==119;target=T[m];available=np.isfinite(ov[i])&(ov[i]>0)
 assert not np.any((target>0)&~available);assert not np.any((prev>0)&~available)
 mark=cv[j] if terminal else ov[j];rel=np.divide(mark,ov[i],out=np.ones(N),where=available&np.isfinite(mark))-1
 assert not np.any((target>0)&~np.isfinite(mark))
 fee,turn=orig.rebalance(prev,target);gross=1+target@rel;net=(1-fee)*gross-1
 stop=j+1 if terminal else j;marks=cv[i:stop]/ov[i]
 assert not np.any((target[:,None,:]>0)&~np.isfinite(marks[None,:,:]))
 dy=nav[:,None]*(1-fee[:,None])*(1+target@np.nan_to_num(marks-1).T)
 daily.extend(dy.T);nav*=1+net;daily.append(nav.copy());prev=target*(1+rel)/gross[:,None]
 for a in range(2*R):rows.append(dict(strategy=rules[a%R][0],kind='selected' if a<R else 'matched_control',execution_date=str(pd.Timestamp(dates[m]).date()),end_date=str(idx[j].date()),terminal_close=terminal,count=int((target[a]>0).sum()),exposure=float(target[a].sum()),gross_return=gross[a]-1,net_return=net[a],fee=fee[a],turnover=turn[a],nav=nav[a]))
z=pd.DataFrame(rows);z.to_csv(P/'monthly.csv',index=False);daily=np.array(daily)
np.savez_compressed(P/'daily_nav.npz',nav=daily)
def metrics(g,ds=None,ss=None):
 r=g.net_return.to_numpy();w=np.r_[1,np.cumprod(1+r)];sd=r.std(ddof=1);n=len(r)
 return dict(months=n,cagr=w[-1]**(252/ss if ss else 12/n)-1,total_return=w[-1]-1,mdd=1-np.min((np.r_[1,ds] if ds is not None else w)/np.maximum.accumulate(np.r_[1,ds] if ds is not None else w)),monthly_mdd=1-np.min(w/np.maximum.accumulate(w)),sharpe=r.mean()/sd*np.sqrt(12) if sd else np.nan,active_months=int(g['count'].gt(0).sum()),stock_months=int(g['count'].sum()),mean_monthly_count=g['count'].mean(),mean_exposure=g.exposure.mean(),turnover=g.turnover.sum(),fees=g.fee.sum())
out=[];annual=[];slices=[]
for a,(rid,ids) in enumerate(rules):
 g=z[(z.strategy==rid)&z.kind.eq('selected')];b=z[(z.strategy==rid)&z.kind.eq('matched_control')];active=g['count'].to_numpy()>0
 q=dict(strategy=rid,order=len(ids),definition=' AND '.join(f'{panel[i][0]} {panel[i][1]} {panel[i][2]}' for i in ids) or 'original RSI control',**metrics(g,daily[:,a],sessions))
 q.update({'matched_'+k:v for k,v in metrics(b,daily[:,a+R],sessions).items()});q['cagr_minus_matched']=q['cagr']-q['matched_cagr'];q['active_month_mean_net']=g.net_return.to_numpy()[active].mean() if active.any() else np.nan;q['active_matched_mean_net']=b.net_return.to_numpy()[active].mean() if active.any() else np.nan;q['active_gross_excess']=np.mean((g.gross_return.to_numpy()-b.gross_return.to_numpy())[active]) if active.any() else np.nan
 out.append(q)
 for yr in range(2009,2019):
  for kind,gg in [('selected',g),('matched_control',b)]:
   h=gg[pd.to_datetime(gg.execution_date).dt.year.eq(yr)];annual.append(dict(strategy=rid,kind=kind,year=yr,**metrics(h)))
 for label,ys in [('2009',[2009]),('2011',[2011]),('2015-16',[2015,2016]),('2018',[2018])]:
  for kind,gg in [('selected',g),('matched_control',b)]:slices.append(dict(strategy=rid,kind=kind,slice=label,**metrics(gg[pd.to_datetime(gg.execution_date).dt.year.isin(ys)])))
r=pd.DataFrame(out).sort_values(['cagr','strategy'],ascending=[False,True]);r.insert(0,'rank',range(1,len(r)+1));r.to_csv(P/'full_ranked.csv',index=False);pd.DataFrame(annual).to_csv(P/'annual.csv',index=False);pd.DataFrame(slices).to_csv(P/'year_slices.csv',index=False)
original=pd.read_csv(E/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/monthly.csv')
control=z[z.strategy.eq('control')&z.kind.eq('selected')]
np.testing.assert_allclose(control.net_return,original.strategy_return,atol=1e-12)
base=r[r.strategy.eq('control')].iloc[0];assert abs(base.cagr-0.23193680384098725)<1e-12
assert x.feature_date.lt(x.execution_date).all();assert d.date.max()<pd.Timestamp('2019-01-01')
audit=dict(counts_by_order={str(k):sum(len(ids)==k for _,ids in rules) for k in range(4)},baseline_cagr=base.cagr,baseline_max_monthly_error=float(np.max(abs(control.net_return.to_numpy()-original.strategy_return.to_numpy()))),sessions=int(sessions),months=120,candidates=len(x),data_max=str(d.date.max()),plan_sha256=hashlib.sha256((P/'PLAN.md').read_bytes()).hexdigest(),source_features_sha256=hashlib.sha256((E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv').read_bytes()).hexdigest())
(P/'audit.json').write_text(json.dumps(audit,indent=2))
report='# RSI + fixed indicator combinations, exploratory 2009–2018\n\nExecuted all 129 combinations: 9 singles, 36 pairs, 84 triples, plus original control. Definitions and hypotheses were saved in PLAN.md before outcome computation. No outcome-based eligibility, support filter, threshold fitting, GA, production changes or 2019+ rows. All combinations ranked in full_ranked.csv, including sparse and losing rows.\n\n'
report+=f'Original control reconciles every monthly net return (max error {audit["baseline_max_monthly_error"]:.3g}); CAGR {base.cagr:.6%}, daily MDD {base.mdd:.4%}, monthly Sharpe {base.sharpe:.4f}, {int(base.stock_months)} stock-months. Original CAGR uses 252/{sessions} session annualization.\n\n'
report+='Accounting follows original exactly, including December 31, 2018 terminal CLOSE rather than January 2019 open; no terminal liquidation. Other intervals are open-to-open. A strictly open-to-open full December result is unavailable without forbidden 2019 data. Empty cash earns zero gross return; selling into cash incurs the original commission. PLAN.md documents exact fees and feature definitions.\n\n|Rank|Rule|CAGR|Daily MDD|Sharpe|Active months|Stock-months|Matched-control CAGR|\n|---:|---|---:|---:|---:|---:|---:|---:|\n'
for a in r.head(12).itertuples():report+=f'|{a.rank}|{a.strategy}|{a.cagr:.2%}|{a.mdd:.2%}|{a.sharpe:.2f}|{a.active_months}|{a.stock_months}|{a.matched_cagr:.2%}|\n'
report+='\nThese are descriptive leaders after 129 dependent tests, not validated alpha. Entire 2009–2018 is exploratory in-sample. No blind or independent holdout claim. Prior feature exploration adds unquantified researcher selection. Fixed historical 77-ticker universe has survivorship/availability bias, uncertain delisting coverage and vendor adjustment provenance; vendor volume can be split-sensitive.\n\nEach matched control uses the original basket on exactly the selected strategy active months and cash otherwise, including its own drift and transaction costs. This matches binary capital exposure, not volatility, beta or stock count. CAGR-minus-matched and active-month net means/gross excess separate selection evidence from cash timing; active averages are descriptive and omit cash-transition sale costs on inactive months. No active-month CAGR is mislabeled as calendar performance.\n\nmonthly.csv supplies every portfolio/month count, exposure, net/gross returns, fees and NAV. selections.csv and candidate_flags.csv expose all decisions. annual.csv supplies continuous-path year segments for all strategies and matched controls; year_slices.csv explicitly includes 2009, 2011, 2015–16, 2018. Annual/slice CAGR uses 12/months and MDD is monthly; full ranked MDD uses daily close marks plus opening endpoints. Full CAGR uses original session convention. daily_nav.npz columns follow control then itertools combination order, then matched controls in same order. Full rankings are available regardless of headline table. Verification independently replays monthly dollar accounting and exact memberships.\n'
report+='\n|Order|Tested|Above original CAGR|Median CAGR|Minimum CAGR|Maximum CAGR|\n|---:|---:|---:|---:|---:|---:|\n'
for k in [1,2,3]:
 gg=r[r.order.eq(k)];report+=f'|{k}|{len(gg)}|{int(gg.cagr.gt(base.cagr).sum())}|{gg.cagr.median():.2%}|{gg.cagr.min():.2%}|{gg.cagr.max():.2%}|\n'
report+='\nYear slices below use the CAGR leader descriptively; all rules and matched controls are in year_slices.csv. Return is cumulative net return, not annualized for 2015–16.\n\n|Slice|Portfolio|Net return|Exposure|Stock-months|\n|---|---|---:|---:|---:|\n'
sl=pd.DataFrame(slices)
for label in ['2009','2011','2015-16','2018']:
 for rid,kind in [('control','selected'),(r.iloc[0].strategy,'selected'),(r.iloc[0].strategy,'matched_control')]:
  v=sl[sl['slice'].eq(label)&sl.strategy.eq(rid)&sl.kind.eq(kind)].iloc[0];report+=f'|{label}|{rid} {kind}|{v.total_return:.2%}|{v.mean_exposure:.2%}|{int(v.stock_months)}|\n'
(P/'REPORT.md').write_text(report)
print(json.dumps(audit,indent=2))
