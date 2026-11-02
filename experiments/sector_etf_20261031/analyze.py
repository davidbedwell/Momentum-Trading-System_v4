#!/usr/bin/env python3
"""Frozen local-cache analysis. Discovery and validation require separate commands."""
import argparse, datetime as dt, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm, rankdata
import pyarrow.parquet as pq
from run import verify_protocol, INCEPTION, SECTORS
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'/'analysis'
SPLITS={'discovery':('2000-01-01','2016-12-31'),'discovery_early':('2000-01-01','2008-12-31'),'discovery_late':('2009-01-01','2016-12-31'),'validation':('2017-01-01','2025-12-31'),'validation_early':('2017-01-01','2020-12-31'),'validation_late':('2021-01-01','2025-12-31'),'full':('2000-01-01','2025-12-31')}
ENDPOINTS=[('H1_1m',6,1),('H1_3m',6,3),('H2_1m',12,1),('H2_3m',12,3),('H3_1m',1,1)]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,indent=2,allow_nan=False,default=str)+'\n')
def clean(x):
 if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
 if isinstance(x,list): return [clean(v) for v in x]
 if isinstance(x,(float,np.floating)) and not np.isfinite(x): return None
 if isinstance(x,np.generic): return x.item()
 return x

def load():
 verify_protocol(); frames=[]; audit=[]
 paths=[ROOT/'data/legacy_sector_etf_panel_2005_2026.parquet',ROOT/'data/sector_etf_extension_xlre_xlc_yfinance_20261007.parquet',Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')]
 for p in paths:
  d=pd.read_parquet(p);d['date']=pd.to_datetime(d.date).dt.normalize()
  if 'ticker' not in d: d['ticker']='SPY'
  assert {'date','ticker','adj_close','close'}<=set(d.columns)
  assert not d.duplicated(['date','ticker']).any()
  assert np.isfinite(d.adj_close).all() and (d.adj_close>0).all()
  rec={'path':str(p),'sha256':sha(p),'rows':len(d),'parquet_metadata_keys':[k.decode() for k in (pq.ParquetFile(p).metadata.metadata or {})],'schema':{c:str(t) for c,t in d.dtypes.items()},'symbols':{}}
  for s,g in d.groupby('ticker'):
   assert (g.date>=pd.Timestamp(INCEPTION[s])).all(),f'{s} pre-inception'
   assert g.date.is_monotonic_increasing
   rec['symbols'][s]={'first':str(g.date.min().date()),'last':str(g.date.max().date()),'rows_through_2025':int((g.date<'2026').sum()),'adjustment_factor_min':float((g.adj_close/g.close).min()),'adjustment_factor_max':float((g.adj_close/g.close).max())}
  audit.append(rec);frames.append(d[d.date<'2026'][['date','ticker','adj_close']])
 d=pd.concat(frames);assert not d.duplicated(['date','ticker']).any()
 p=d.pivot(index='date',columns='ticker',values='adj_close').sort_index()
 calendar=p.SPY.dropna().index;p=p.reindex(calendar)
 missing={}
 for s in p:
  a=p[s].dropna(); interior=p.loc[a.index.min():a.index.max(),s]
  missing[s]=int(interior.isna().sum())
  assert not interior.isna().any(),f'{s} internal gaps'
 assert set(SECTORS+['SPY'])==set(p.columns)
 write(OUT/'data_audit.json',{'files':audit,'internal_missing_sessions':missing,'excluded_2026':True,'adjustment_evidence':'Explicit vendor-cache adj_close; sector files lack corporate-action ledger and acquisition metadata. Dividend/split correctness cannot be independently reconciled. Raw opens not used.','limitations':['No 2000-2004 sector observations; earliest sector observation 2005-09-01.','No supplied SGOV; hybrid H4 blocked. Cash-only sensitivity executed.']})
 return p

def block_indices(n,rng,reps=2000):
 starts=rng.integers(0,n,size=(reps,int(np.ceil(n/12))))
 return ((starts[:,:,None]+np.arange(12))%n).reshape(reps,-1)[:,:n]
def inference(x):
 x=np.asarray(x,float);x=x[np.isfinite(x)];n=len(x)
 if n<2:return {'n':n,'mean':float(x.mean()) if n else None,'hac_p':None,'ci_low':None,'ci_high':None}
 z=x-x.mean();v=np.dot(z,z)/n
 for lag in range(1,min(6,n-1)+1):v+=2*(1-lag/7)*np.dot(z[lag:],z[:-lag])/n
 se=np.sqrt(max(v,0)/n);pv=2*norm.sf(abs(x.mean()/se)) if se else float(x.mean()==0)
 means=x[block_indices(n,np.random.default_rng(20261031))].mean(axis=1)
 lo,hi=np.quantile(means,[.025,.975])
 return dict(n=n,mean=float(x.mean()),hac_se=float(se),hac_p=float(pv),ci_low=float(lo),ci_high=float(hi))
def holm(ps):
 ps=np.asarray(ps,float);order=np.argsort(ps);res=np.empty(len(ps));last=0
 for k,i in enumerate(order):last=max(last,min(1,(len(ps)-k)*ps[i]));res[i]=last
 return res

def signals(p):
 months=p.groupby(p.index.to_period('M')).tail(1).index
 rows=[];targets={}
 for label,look,horizon in ENDPOINTS:
  ts={}
  for day in months:
   cutoff=day-pd.DateOffset(months=look)
   hist=p.index[p.index<=cutoff]
   if not len(hist):continue
   old=hist[-1];s=[]
   for ticker in SECTORS:
    a,b=p.at[old,ticker],p.at[day,ticker]
    if pd.notna(a) and pd.notna(b):
     score=(b/a)/(p.at[day,'SPY']/p.at[old,'SPY'])-1
     s.append((ticker,-score if look==1 else score))
   if len(s)<9:continue
   s.sort(key=lambda t:(-t[1],t[0]));top=[t[0] for t in s[:3]];bottom=[t[0] for t in s[-3:]]
   execution=p.index.searchsorted(day)+1
   if execution>=len(p):continue
   ts[p.index[execution]]={'top':top,'bottom':bottom,'eligible':[t[0] for t in s],'signal':day}
   target_period=day.to_period('M')+horizon
   ends=months[months.to_period('M')==target_period]
   if not len(ends):continue
   end=ends[0];ex_end=p.index.searchsorted(end)+1
   # Predictive labels are signal-close to future signal-close; trading is separately delayed.
   y=np.array([(p.at[end,t]/p.at[day,t])/(p.at[end,'SPY']/p.at[day,'SPY'])-1 for t,_ in s])
   scores=np.array([v for _,v in s]);ic=np.corrcoef(rankdata(scores),rankdata(y))[0,1]
   total=np.array([p.at[end,t]/p.at[day,t]-1 for t,_ in s])
   rows.append({'endpoint':label,'signal':day,'label_end':end,'n_sectors':len(s),'ic':ic,'spread_gross':total[:3].mean()-total[-3:].mean()})
  targets[label]=ts
 return pd.DataFrame(rows),targets

def simulate(p,targets,kind,cost,start,end):
 # A period starts in cash at the close preceding its first return. Carry the latest
 # known executable target into that close, pay entry, and liquidate at final close.
 eligible_start=pd.Timestamp(start)
 if targets:
  first=min(targets)
  pos=p.index.searchsorted(first)+1
  if pos<len(p):eligible_start=max(eligible_start,p.index[pos])
 if kind=='H4':eligible_start=max(eligible_start,p.index[201])
 ix=p.index[(p.index>=eligible_start)&(p.index<=end)]
 if len(ix)<2:return None
 prior=p.index.searchsorted(ix[0])-1
 if prior<0:ix=ix[1:];prior=0
 dates=p.index[prior:p.index.searchsorted(ix[-1])+1];a=p.reindex(dates).to_numpy();cols=list(p.columns)
 h=np.zeros(len(cols));cash=1.;wealth=1.;rets=[];turn=[]
 target_dates=sorted(targets) if targets is not None else []
 def target(day):
  w=np.zeros(len(cols))
  if kind=='SPY':w[cols.index('SPY')]=1
  elif kind=='cash':pass
  elif kind=='H4':
   j=p.index.searchsorted(day)-1
   if j>=199 and p.SPY.iloc[j]>p.SPY.iloc[j-199:j+1].mean():w[cols.index('SPY')]=1
  else:
   available=[t for t in target_dates if t<=day]
   if available:
    t=targets[available[-1]]
    if kind=='spread':
     for s in t['top']:w[cols.index(s)]=1/3
     for s in t['bottom']:w[cols.index(s)]=-1/3
    else:
     names=t['eligible'] if kind=='equal' else t['top']
     for s in names:w[cols.index(s)]=1/len(names)
  return w
 def rebalance(w):
  nonlocal h,cash,wealth
  # Self-financing target weights after costs, solved by fixed point.
  net=wealth
  for _ in range(30):net=wealth-cost*np.abs(w*net-h).sum()
  traded=np.abs(w*net-h).sum();h=w*net;cash=net-h.sum();wealth=net
  return traded
 entry=rebalance(target(dates[0]));pending_cost=1-wealth
 for j,day in enumerate(dates[1:],1):
  before=1. if j==1 else wealth
  ratio=np.divide(a[j],a[j-1],out=np.ones(len(cols)),where=np.isfinite(a[j])&np.isfinite(a[j-1]))
  h*=ratio;wealth=cash+h.sum();traded=entry if j==1 else 0.
  if kind=='H4' or (kind not in ['SPY','cash'] and day in targets):traded+=rebalance(target(day))
  if j==len(dates)-1:
   traded+=np.abs(h).sum();wealth-=cost*np.abs(h).sum();h[:]=0;cash=wealth
  rets.append(wealth/before-1);turn.append(traded/before)
 result=pd.DataFrame({'return':rets,'turnover':turn},index=dates[1:])
 result.attrs['initial_close']=dates[0]
 return result
def metrics(d):
 r=d['return'];w=np.r_[1,np.cumprod(1+r.to_numpy())];years=(d.index[-1]-d.attrs.get('initial_close',d.index[0]-pd.Timedelta(days=1))).days/365.25
 c=w[-1]**(1/years)-1;m=float(np.min(w/np.maximum.accumulate(w)-1))
 return {'first_return':str(d.index[0].date()),'last_return':str(d.index[-1].date()),'days':len(d),'cagr':c,'mdd':m,'calmar':c/abs(m) if m else None,'annualized_vol':r.std(ddof=1)*np.sqrt(252),'annual_turnover':d.turnover.sum()/years,'total_return':w[-1]-1}
def paired(h,b):
 # Resample paired whole daily month blocks to retain intra-month drawdowns.
 df=pd.concat([h['return'].rename('h'),b['return'].rename('b')],axis=1).dropna();groups=[g.to_numpy() for _,g in df.groupby(df.index.to_period('M'))]
 inds=block_indices(len(groups),np.random.default_rng(20261031));out=[]
 for ids in inds:
  a=np.concatenate([groups[i] for i in ids]);w=np.vstack([np.ones(2),np.cumprod(1+a,axis=0)])
  c=w[-1]**(252/len(a))-1;dd=np.min(w/np.maximum.accumulate(w,axis=0)-1,axis=0)
  out.append([c[0]-c[1],abs(dd[1])-abs(dd[0])])
 out=np.asarray(out);res={}
 for j,n in enumerate(['cagr_difference','absolute_mdd_improvement']):
  lo,hi=np.quantile(out[:,j],[.025,.975]);pv=min(1,2*min((np.sum(out[:,j]<=0)+1)/2001,(np.sum(out[:,j]>=0)+1)/2001))
  res[n]={'ci_low':lo,'ci_high':hi,'bootstrap_p':pv}
 hp=holm([res[n]['bootstrap_p'] for n in res])
 for n,v in zip(res,hp):res[n]['holm_p']=v
 return res

def run(stage):
 OUT.mkdir(exist_ok=True,parents=True)
 if stage=='validation':
  seal=json.loads((OUT/'discovery_seal.json').read_text())
  for f,v in seal['hashes'].items():assert sha(ROOT/f)==v,f'Seal mismatch {f}'
 p=load();diag,targets=signals(p)
 # No future outcomes are used by signal construction. Discovery stage masks labels
 # before inference; holdout statistics and portfolios are created only explicitly.
 splits=['discovery','discovery_early','discovery_late'] if stage=='discovery' else ['validation','validation_early','validation_late','full']
 stats=[];perf=[];active=[];h4=[]
 for split in splits:
  start,end=SPLITS[split];print('Computing',split,flush=True)
  selected=diag[(diag.signal>=start)&(diag.label_end<=end)&(diag.signal<=end)].copy()
  selected.to_csv(OUT/f'{split}_monthly_diagnostics.csv',index=False)
  local=[]
  for endpoint,_,_ in ENDPOINTS:
   z=selected[selected.endpoint==endpoint]
   ic=inference(z.ic);spread=inference(z.spread_gross)
   local.append({'split':split,'endpoint':endpoint,**{'ic_'+k:v for k,v in ic.items()},**{'spread_'+k:v for k,v in spread.items()}})
  adj=holm([r['ic_hac_p'] if r['ic_hac_p'] is not None else 1 for r in local])
  for r,v in zip(local,adj):r['ic_holm_p']=float(v)
  stats+=local
  for cost in [.0015,.003]:
   series={}
   base_targets={}
   for day in p.groupby(p.index.to_period('M')).tail(1).index:
    pos=p.index.searchsorted(day)+1
    names=[s for s in SECTORS if pd.notna(p.at[day,s])]
    if pos<len(p) and len(names)>=9:base_targets[p.index[pos]]={'eligible':names}
   for strategy,kind,t in [('SPY','SPY',None),('cash','cash',None),('H4_cash','H4',None),('equal_weight','equal',base_targets)]+[(f'{h}_{k}',k,targets[h+'_1m']) for h in ['H1','H2','H3'] for k in ['top','spread']]:
    d=simulate(p,t,kind,cost,start,end)
    if d is None:continue
    series[strategy]=d
    perf.append({'split':split,'strategy':strategy,'cost_bps':int(cost*10000),**metrics(d)})
    d.to_csv(OUT/f'{split}_{strategy}_{int(cost*10000)}bps_daily.csv',index_label='date')
   for h in ['H1','H2','H3']:
    a=series[h+'_top']['return']
    matched=simulate(p,None,'SPY',cost,str(a.index[0].date()),end)
    b=matched['return'].reindex(a.index)
    perf.append({'split':split,'strategy':h+'_matched_SPY','cost_bps':int(cost*10000),**metrics(matched)})
    # Match benchmark inception to each strategy's valid lookback, no idle warmup dilution.
    monthly_a=(1+a).groupby(a.index.to_period('M')).prod()-1
    monthly_b=(1+b).groupby(b.index.to_period('M')).prod()-1
    active.append({'split':split,'strategy':h,'cost_bps':int(cost*10000),**inference(monthly_a-monthly_b)})
    spread_r=series[h+'_spread']['return']
    spread_m=(1+spread_r).groupby(spread_r.index.to_period('M')).prod()-1
    active.append({'split':split,'strategy':h+'_net_spread','cost_bps':int(cost*10000),**inference(spread_m)})
   hb=simulate(p,None,'SPY',cost,str(series['H4_cash'].index[0].date()),end)
   perf.append({'split':split,'strategy':'H4_matched_SPY','cost_bps':int(cost*10000),**metrics(hb)})
   h4.append({'split':split,'cost_bps':int(cost*10000),**paired(series['H4_cash'],hb)})
 pd.DataFrame(stats).to_csv(OUT/f'{stage}_inference.csv',index=False)
 pd.DataFrame(perf).to_csv(OUT/f'{stage}_performance.csv',index=False)
 pd.DataFrame(active).to_csv(OUT/f'{stage}_active_inference.csv',index=False)
 write(OUT/f'{stage}_h4_paired.json',clean(h4))
 write(OUT/f'{stage}_execution.json',{'completed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'stage':stage,'protocol_sha256':verify_protocol()['sha256'],'signal_implementation':'last observed close on/before calendar lookback; minimum nine with full observed lookback','execution':'next session close; weights drift; entry and exit included; raw opens unused','predictive_labels':'signal close to future month-end close; labels crossing splits excluded','bootstrap_reps':2000,'bootstrap_seed':20261031,'data_audit_sha256':sha(OUT/'data_audit.json')})
 if stage=='discovery':
  files=[ROOT/'analyze.py',ROOT/'run.py',ROOT/'PREREGISTRATION.md',ROOT/'preregistration.lock.json']+list(OUT.glob('discovery*'))+[OUT/'data_audit.json']
  write(OUT/'discovery_seal.json',{'sealed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'validation_outcomes_opened':False,'hashes':{str(f.relative_to(ROOT)):sha(f) for f in files if f.name!='discovery_seal.json'}})
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['discovery','validation']);run(a.parse_args().stage)
