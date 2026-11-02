"""Frozen DEV87 transfer; no search, fitting or parameter changes."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']: os.environ[k]='1'
import pandas as pd, numpy as np, json, hashlib, importlib.util
from pathlib import Path
P=Path(__file__).resolve().parent; E=P.parent
sp=importlib.util.spec_from_file_location('orig',E/'dev79_monthly_indicator_20261101/indicator_experiment.py'); orig=importlib.util.module_from_spec(sp);sp.loader.exec_module(orig)
RULES=['control','k2_2-4','k1_4','k1_1','k2_1-2']
DEFS=['RSI14 lowest 20%','ma_distance_20 < 0 AND acceleration_21 > 0','acceleration_21 > 0','return_252 > 0','return_252 > 0 AND ma_distance_20 < 0']
def digest(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def panels(d):
 d=d.copy();d.date=pd.to_datetime(d.date);assert not d.duplicated(['date','ticker']).any()
 c=d.pivot(index='date',columns='ticker',values='adj_close').sort_index().sort_index(axis=1)
 return c,d.pivot(index='date',columns='ticker',values='open').reindex_like(c)*c/d.pivot(index='date',columns='ticker',values='close').reindex_like(c)
def features(c):
 delta=c.diff(); g=delta.clip(lower=0).ewm(alpha=1/14,adjust=False,min_periods=14).mean(); l=(-delta.clip(upper=0)).ewm(alpha=1/14,adjust=False,min_periods=14).mean()
 return {'rsi14':100-100/(1+g/l),'return_252':c/c.shift(252)-1,'ma_distance_20':c/c.rolling(20).mean()-1,'acceleration_21':c/c.shift(21)-c.shift(21)/c.shift(42)}
def flags(v):
 r,m,a=v['return_252'],v['ma_distance_20'],v['acceleration_21']
 pos=lambda x: np.isfinite(x)&(x>0)
 neg=lambda x: np.isfinite(x)&(x<0)
 return [np.ones_like(r,dtype=bool),neg(m)&pos(a),pos(a),pos(r),pos(r)&neg(m)]
errors={}; audits={}; allmetrics=[]; annual=[]
d=pd.read_parquet(P/'dev87_raw.parquet'); dev=pd.read_parquet(orig.SOURCE)
for label,frame in [('dev87',d),('dev79',dev)]:
 frame.groupby('ticker').agg(start=('date','min'),end=('date','max'),bars=('date','size')).to_csv(P/f'{label}_coverage.csv')
 frame[[k for k in ['ticker','security_id','yahoo_symbol'] if k in frame]].drop_duplicates().to_csv(P/f'{label}_identities.csv',index=False)
normalize=lambda t: str(t).upper().strip().replace('.','-').replace('/','-')
a=set(dev.ticker);b=set(d.ticker); overlap=sorted(a&b); normalized=sorted(set(map(normalize,a))&set(map(normalize,b)))
yahoo_overlap=sorted(set(map(normalize,d.yahoo_symbol.dropna()))&set(map(normalize,a)))
identity=set(dev.security_id.dropna().astype(str))&set(d.security_id.dropna().astype(str))
pd.DataFrame({'ticker':overlap}).to_csv(P/'overlap_tickers.csv',index=False)
pd.DataFrame({'security_id':sorted(identity)}).to_csv(P/'overlap_security_ids.csv',index=False)
audits['overlap']={'exact_tickers':overlap,'normalized_tickers':normalized,'yahoo_symbol_overlap':yahoo_overlap,'security_ids':sorted(identity),'independent_stock_holdout':not bool(overlap or normalized or yahoo_overlap or identity),'identity_note':'Compared supplied security_id and DEV87 yahoo_symbol mappings; no external corporate-action identity registry available.'}
# Reconstruct DEV79 using data strictly before 2019, reconcile original source engine and saved development outputs.
c79,o79=panels(dev[dev.date<pd.Timestamp('2019-01-01')]); f79=features(c79)
m79,t79,h79,_=orig.replay(c79,o79,-f79['rsi14'],'2009-01-01','2018-12-31')
saved=pd.read_csv(E/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/monthly.csv')
errors['dev79_monthly']=float(np.max(abs(t79.strategy_return-saved.strategy_return)))
errors['dev79_cagr']=abs(m79['cagr']-0.23193680384098725)
hsaved=pd.read_csv(E/'dev79_monthly_indicator_20261101/adjusted/discovery/rsi14_oversold/holdings.csv')
assert list(zip(h79.execution_date,h79.ticker))==list(zip(hsaved.execution_date,hsaved.ticker))
xf=pd.read_csv(E/'dev79_rsi_winner_characteristics_20261101/stock_month_features.csv')
for k in f79:
 vals=[f79[k].at[pd.Timestamp(row.feature_date),row.ticker] for row in xf.itertuples()]
 errors['dev79_feature_'+k]=float(np.nanmax(abs(np.array(vals)-xf[k].to_numpy())))
audits['dev79_control']={'cagr':m79['cagr'],'tickers_before_2019':len(c79.columns),'memberships_match':True}
for era,start,end in [('2009-2018','2009-01-01','2018-12-31'),('2019-2025','2019-01-01','2025-12-31')]:
 dest=P/era;dest.mkdir(exist_ok=True)
 c,o=panels(d[d.date<=pd.Timestamp(end)]);f=features(c);cv=c.to_numpy();ov=o.to_numpy();ix=c.index;N=len(c.columns)
 run=np.flatnonzero((ix>=start)&(ix<=end));assert len(run)>0
 starts=[i for i in run if i==run[0] or ix[i].to_period('M')!=ix[i-1].to_period('M')];last=run[-1]
 assert len(starts)==(120 if era=='2009-2018' else 84)
 T=[];candidates=[];selections=[];cancel=0;eligible_rows=[];feature_error=0.
 for i in starts:
  assert i>0
  sig=-f['rsi14'].iloc[i-1].to_numpy(); valid=np.isfinite(cv[i-1])&(cv[i-1]>0)&np.isfinite(sig)
  ids=np.flatnonzero(valid);chosen=ids[np.argsort(-sig[ids],kind='stable')[:max(1,len(ids)//5)]] if len(ids) else ids
  v={k:z.iloc[i-1].to_numpy() for k,z in f.items()};fl=flags(v);targets=np.zeros((5,N))
  # Independent stable Python sorting verifies RSI candidate selection.
  check=sorted([n for n in range(N) if valid[n]],key=lambda n:(-sig[n],str(c.columns[n])))[:max(1,len(ids)//5)]
  assert chosen.tolist()==check
  for n in chosen:
   rec=dict(execution_date=str(ix[i].date()),feature_date=str(ix[i-1].date()),ticker=c.columns[n],**{k:float(z[n]) for k,z in v.items()})
   # Re-evaluate lag/rolling predicates from literal historical slices.
   series=cv[:i,n];rr=series[-1]/series[-253]-1 if len(series)>=253 else np.nan;mm=series[-1]/np.mean(series[-20:])-1 if len(series)>=20 else np.nan;aa=series[-1]/series[-22]-series[-22]/series[-43] if len(series)>=43 else np.nan
   for k,value in [('return_252',rr),('ma_distance_20',mm),('acceleration_21',aa)]:
    assert np.isfinite(value)==np.isfinite(v[k][n])
    if np.isfinite(value):feature_error=max(feature_error,abs(value-v[k][n]))
   independent=[True,np.isfinite(mm) and mm<0 and np.isfinite(aa) and aa>0,np.isfinite(aa) and aa>0,np.isfinite(rr) and rr>0,np.isfinite(rr) and rr>0 and np.isfinite(mm) and mm<0]
   for q,rid in enumerate(RULES):assert bool(fl[q][n])==independent[q];rec[rid]=bool(fl[q][n])
   candidates.append(rec)
  for q in range(5):
   take=chosen[fl[q][chosen]]
   if len(take):targets[q,take]=1/len(take)
   for n in take:selections.append(dict(strategy=RULES[q],execution_date=str(ix[i].date()),ticker=c.columns[n],requested_weight=targets[q,n],executed=bool(np.isfinite(ov[i,n]) and ov[i,n]>0)))
  eligible_rows.append(dict(execution_date=str(ix[i].date()),eligible=len(ids),candidates=len(chosen)))
  targets=np.concatenate([targets,np.where(targets.sum(axis=1,keepdims=True)>0,targets[0:1],0)])
  available=np.isfinite(ov[i])&(ov[i]>0);cancel+=int(((targets>0)&~available).sum());targets[:,~available]=0;T.append(targets)
 pd.DataFrame(candidates).to_csv(dest/'candidate_features_flags.csv',index=False);pd.DataFrame(selections).to_csv(dest/'selections.csv',index=False);pd.DataFrame(eligible_rows).to_csv(dest/'eligibility.csv',index=False)
 prev=np.zeros((10,N));nav=np.ones(10);shares=np.zeros((10,N));cash=np.ones(10);monthly=[];daily=[];dollar_error=0.;fee_error=0.;rebalance_error=0.
 for m,i in enumerate(starts):
  j=starts[m+1] if m+1<len(starts) else last;terminal=m+1==len(starts);target=T[m];avail=np.isfinite(ov[i])&(ov[i]>0)
  assert not np.any((prev>0)&~avail)
  mark=cv[j] if terminal else ov[j];assert not np.any((target>0)&(~np.isfinite(mark)|(mark<=0)))
  rel=np.divide(mark,ov[i],out=np.ones(N),where=avail&np.isfinite(mark))-1
  fee,turn=orig.rebalance(prev,target);gross=1+target@rel;net=(1-fee)*gross-1
  # Independent dollar holdings/cash ledger; solve commission by bisection.
  oldval=shares*np.where(avail,ov[i],0);pre=cash+oldval.sum(axis=1)
  dollar_error=max(dollar_error,float(np.max(abs(pre-nav))))
  low=np.zeros(10);high=pre.copy()
  for _ in range(70):
   post=(low+high)/2;res=post+.001*np.abs(target*post[:,None]-oldval).sum(axis=1)-pre
   high=np.where(res>0,post,high);low=np.where(res<=0,post,low)
  post=(low+high)/2;fee_error=max(fee_error,float(np.max(abs((pre-post)/pre-fee))))
  values=target*post[:,None];shares=np.divide(values,ov[i],out=np.zeros_like(values),where=avail);cash=post-values.sum(axis=1)
  rebalance_error=max(rebalance_error,float(np.max(abs(post+ .001*np.abs(values-oldval).sum(axis=1)-pre))))
  stop=j+1 if terminal else j
  for k in range(i,stop):
   assert not np.any((target>0)&(~np.isfinite(cv[k])|(cv[k]<=0)))
   dn=nav*(1-fee)*(1+target@np.nan_to_num(cv[k]/ov[i]-1));ind=cash+(shares*np.nan_to_num(cv[k])).sum(axis=1)
   dollar_error=max(dollar_error,float(np.max(abs(dn-ind))))
   daily.append(dict(date=str(ix[k].date()),mark='close',**{f'{kind}:{RULES[q%5]}':dn[q] for q,kind in enumerate(['selected']*5+['matched_control']*5)}))
  nav*=1+net;ind=cash+(shares*np.nan_to_num(mark)).sum(axis=1);dollar_error=max(dollar_error,float(np.max(abs(nav-ind))))
  daily.append(dict(date=str(ix[j].date()),mark='terminal_close' if terminal else 'open',**{f'{kind}:{RULES[q%5]}':nav[q] for q,kind in enumerate(['selected']*5+['matched_control']*5)}))
  prev=target*(1+rel)/gross[:,None]
  for q in range(10):monthly.append(dict(strategy=RULES[q%5],kind='selected' if q<5 else 'matched_control',execution_date=str(ix[i].date()),feature_date=str(ix[i-1].date()),end_date=str(ix[j].date()),terminal_close=terminal,count=int((target[q]>0).sum()),exposure=target[q].sum(),gross_return=gross[q]-1,net_return=net[q],fee=fee[q],turnover=turn[q],nav=nav[q]))
 z=pd.DataFrame(monthly);dy=pd.DataFrame(daily);z.to_csv(dest/'monthly.csv',index=False);dy.to_csv(dest/'daily_nav.csv',index=False)
 for (rid,kind),g in z.groupby(['strategy','kind'],sort=False):
  r=g.net_return.to_numpy();dn=np.r_[1,dy[f'{kind}:{rid}']];wealth=np.prod(1+r)
  met=dict(period=era,strategy=rid,kind=kind,cagr=wealth**(252/len(run))-1,daily_mdd=1-np.min(dn/np.maximum.accumulate(dn)),sharpe=r.mean()/r.std(ddof=1)*np.sqrt(12),total_return=wealth-1,months=len(r),sessions=len(run),active_months=int(g['count'].gt(0).sum()),stock_months=int(g['count'].sum()),mean_exposure=g.exposure.mean(),turnover=g.turnover.sum(),fee_fraction_sum=g.fee.sum());allmetrics.append(met)
  for year,h in g.groupby(pd.to_datetime(g.execution_date).dt.year):annual.append(dict(period=era,strategy=rid,kind=kind,year=int(year),net_return=np.prod(1+h.net_return)-1,active_months=int(h['count'].gt(0).sum()),stock_months=int(h['count'].sum()),mean_exposure=h.exposure.mean()))
 om,ot,oh,_=orig.replay(c,o,-f['rsi14'],start,end)
 control=z[z.strategy.eq('control')&z.kind.eq('selected')]
 errors[era+'_original_monthly']=float(np.max(abs(control.net_return.to_numpy()-ot.strategy_return.to_numpy())))
 errors[era+'_original_mdd']=abs(om['max_drawdown']-next(v['daily_mdd'] for v in allmetrics if v['period']==era and v['strategy']=='control' and v['kind']=='selected'))
 errors[era+'_original_sharpe']=abs(om['monthly_sharpe']-next(v['sharpe'] for v in allmetrics if v['period']==era and v['strategy']=='control' and v['kind']=='selected'))
 errors[era+'_original_cagr']=abs(om['cagr']-next(v['cagr'] for v in allmetrics if v['period']==era and v['strategy']=='control' and v['kind']=='selected'))
 expected=pd.DataFrame(selections);expected=expected[expected.strategy.eq('control')&expected.executed]
 assert sorted(zip(expected.execution_date,expected.ticker))==sorted(zip(oh.execution_date,oh.ticker))
 for q in range(5):
  sg=z[z.strategy.eq(RULES[q])&z.kind.eq('selected')];mg=z[z.strategy.eq(RULES[q])&z.kind.eq('matched_control')];assert np.array_equal(sg.exposure.to_numpy()>0,mg.exposure.to_numpy()>0)
 errors[era+'_dollar_nav']=dollar_error;errors[era+'_fee']=fee_error;errors[era+'_self_financing']=rebalance_error;errors[era+'_feature']=feature_error
 audits[era]={'sessions':len(run),'months':len(starts),'start':str(ix[starts[0]].date()),'end':str(ix[last].date()),'warmup_start':str(ix[0].date()),'tickers':N,'canceled_targets':cancel,'original_control_memberships_match':True,'matched_active_schedule_equal':True,'terminal_liquidation':False}
metrics=pd.DataFrame(allmetrics);metrics.to_csv(P/'metrics.csv',index=False);pd.DataFrame(annual).to_csv(P/'annual.csv',index=False)
assert max(errors.values())<1e-10,errors
sources=[P/'dev87_raw.parquet',orig.SOURCE,P/'FROZEN_SPEC.md',P/'study.py',P/'verify.py',E/'dev79_rsi_indicator_combinations_20261101/study.py',E/'dev79_monthly_indicator_20261101/indicator_experiment.py']
audits.update(status='PASS',verification_errors=errors,source_hashes={str(p):digest(p) for p in sources},versions={'pandas':pd.__version__,'numpy':np.__version__},source_rows=len(d),source_tickers=d.ticker.nunique(),source_start=str(d.date.min()),source_end=str(d.date.max()))
(P/'verification.json').write_text(json.dumps(audits,indent=2))
report='# DEV87 frozen RSI validation — executed and audited\n\n'
report+='Executed only the RSI control and four frozen rules. No fitting, threshold changes, search, GA or production changes. Verification PASS: original-engine monthly control reconciliation, DEV79 reconstruction and memberships/features, independent dollar accounting with bisection fees, screening predicates, matched exposure, endpoints and daily marks. Numerical errors are in verification.json.\n\n'
report+=f'Source contains {d.ticker.nunique()} tickers, {len(d):,} rows, {d.date.min()} through {d.date.max()}. Both requested eras are complete by observed first/last trading sessions and start separately in cash; warmup uses all available preceding observations. Coverage files disclose individual ticker histories.\n\n'
report+=f'Universe overlap: {len(overlap)} exact ticker overlaps, {len(normalized)} normalized overlaps, {len(identity)} shared supplied security IDs with the full 79-ticker DEV79 source (77 pre-2019). Symbol-level stock holdout passes: **{audits["overlap"]["independent_stock_holdout"]}** (including Yahoo symbol aliases). Exact overlaps: '+(', '.join(overlap) or 'none')+'. See overlap lists and identity mappings. Supplied identifiers do not establish exhaustive corporate rename history; no external identity registry was available.\n\n'
report+='Frozen definitions: prior-session RSI14 lowest max(1,floor(eligible/5)), stable ties over sorted tickers; k2_2-4 = MA20 distance < 0 and acceleration21 > 0; k1_4 = acceleration21 > 0; k1_1 = return252 > 0; k2_1-2 = return252 > 0 and MA20 distance < 0. Strict finite predicates, no fill. See FROZEN_SPEC.md for exact formulas.\n\n'
report+='Adjusted open = open × adj_close/close. Monthly equal-weight rebalancing, 10 bp per side on risky trade value, exact self-financing fees, drift between rebalances, cash earns zero. Missing target opens cancel purchases without reallocating; missing held opens or marks fail. December ends at its final close, no liquidation fee or next-January return. Daily MDD includes close marks and next-open endpoints, as in the original engine. CAGR uses 252/session count; Sharpe uses monthly net mean/sample SD × sqrt(12), zero risk-free. Mean exposure is mean monthly target risky exposure. Matched controls use the full RSI basket on exactly the rule’s active months, with their own costs and drift; this matches binary capital exposure, not stock count, beta or risk.\n\n'
for era in ['2009-2018','2019-2025']:
 report+=f'## {era}'+(' — separate later-period transfer' if era=='2019-2025' else ' — frozen primary validation')+'\n\n|Rule|CAGR|Daily MDD|Sharpe|Active months|Stock-months|Exposure|Matched CAGR|Matched MDD|Matched Sharpe|\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n'
 for rid in RULES:
  v=metrics[(metrics.period==era)&(metrics.strategy==rid)&metrics.kind.eq('selected')].iloc[0];b=metrics[(metrics.period==era)&(metrics.strategy==rid)&metrics.kind.eq('matched_control')].iloc[0]
  report+=f'|{rid}|{v.cagr:.2%}|{v.daily_mdd:.2%}|{v.sharpe:.3f}|{int(v.active_months)}/{int(v.months)}|{int(v.stock_months)}|{v.mean_exposure:.2%}|{b.cagr:.2%}|{b.daily_mdd:.2%}|{b.sharpe:.3f}|\n'
 report+='\nAnnual compounded net returns (continuous portfolio path within each era):\n\n|Year|'+'|'.join(RULES)+'|\n|---|'+'---:|'*5+'\n'
 az=pd.DataFrame(annual)
 for yr in sorted(az[az.period.eq(era)].year.unique()):
  report+=f'|{yr}|'+ '|'.join(f'{az[(az.period==era)&(az.year==yr)&az.kind.eq("selected")&az.strategy.eq(rid)].iloc[0].net_return:.2%}' for rid in RULES)+'|\n'
 report+=f'\nCanceled selected/matched target entries: {audits[era]["canceled_targets"]}; sessions: {audits[era]["sessions"]}.\n\n'
report+='Primary-period interpretation: k2_1-2 improves CAGR and drawdown versus the always-invested RSI baseline, but trails its matched control in CAGR (24.41% versus 25.71%). The acceleration rules do not improve baseline CAGR or daily drawdown. In the separate later period, k1_4 has the highest frozen-rule CAGR (25.01%) but daily MDD is 51.09%; no rule is retuned or chosen prospectively from these results.\n\n'
report+='The separate verify.py audits persisted files: source hashes, fees, annual compounding, all portfolio metrics, endpoint labels/NAV, and requested memberships. Its output is artifact_verification.json; run it after study.py.\n\n'
report+='Full selected and matched metrics are in metrics.csv; annual.csv includes both portfolios, active months, stock-months and exposure. Each period directory contains candidate features/flags, requested/executed selections, eligibility, all monthly fees/turnover/net/gross returns and labeled daily NAV. verification.json records source/code/spec SHA256 and numerical reconciliation errors. Reproduce with `/opt/mts/.venv/bin/python experiments/dev87_rsi_frozen_validation_20261101/study.py`.\n\nFixed historical universes retain survivorship/availability bias and uncertain delisting coverage; vendor adjusted prices are not independently point-in-time certified. Frozen rules were selected from DEV79 exploratory results; overlap and prior research prevent treating a contaminated universe as independent confirmation. Later-period results are reported separately without retuning and are not a claim of untouched blind data. Daily MDD follows the original sampled marks, not an intraday high/low loss measure.\n'
(P/'REPORT.md').write_text(report);print(metrics.to_string(index=False));print(json.dumps({'status':'PASS','errors':errors,'overlap':audits['overlap']},indent=2))
