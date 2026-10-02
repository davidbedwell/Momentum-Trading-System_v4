#!/usr/bin/env python3
import argparse,gzip,pickle,json,hashlib,math,heapq
from pathlib import Path
from collections import defaultdict
import numpy as np
SPLIT='2021-09-13'; EXPECT_TRADES=125002; EXPECT_TICKERS=67; CACHE_FMT='MTS_V4_DISCOVERY_RESEARCH_CACHE_V1'
FLOORS=(.25,.50); CAPS=(1.25,1.50,2.00)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(cache,manifest):
 m=json.load(open(manifest)); b=Path(cache).read_bytes()
 if hashlib.sha256(b).hexdigest()!=m['cache_file_sha256']: raise RuntimeError('cache file hash mismatch')
 z=pickle.loads(gzip.decompress(b))
 if (z['format'],z['trade_count'],z['ticker_count'],z['split_date'])!=(CACHE_FMT,EXPECT_TRADES,EXPECT_TICKERS,SPLIT): raise RuntimeError('cache identity mismatch')
 return z,m
def atr_ratio(r): return float(r['atr']/r['ep']) if r.get('atr') is not None and r.get('ep') else math.nan
def prevol(r,n=20):
 a=r['_bars'][max(0,r['si']-n):r['si']]
 if len(a)<10:return math.nan
 c=np.asarray([x['close'] for x in a],float); q=np.diff(np.log(c))
 return float(q.std(ddof=1)) if len(q)>1 else math.nan
def causal_downside(rows,kind,minn=100):
 bydate=defaultdict(list)
 for i,r in enumerate(rows):bydate[r['signal_date']].append(i)
 vals=defaultdict(list);glob=[];pending=[];risk=np.full(len(rows),np.nan)
 for d in sorted(bydate):
  while pending and pending[0][0] < d:
   _,i,key,ret=heapq.heappop(pending);vals[key].append(ret);glob.append(ret)
  inds=bydate[d];gr=None
  if len(glob)>=minn:
   a=np.asarray(glob,float);lo=a[a<0];gr=abs(float(np.quantile(lo,.10))) if len(lo)>=20 else float(a.std(ddof=1))
  cache={}
  for i in inds:
   r=rows[i];key=r['genome'] if kind=='genome' else r['family']
   if key not in cache:
    h=vals[key]
    if len(h)>=minn:
     a=np.asarray(h,float);lo=a[a<0];cache[key]=abs(float(np.quantile(lo,.10))) if len(lo)>=20 else float(a.std(ddof=1))
    else: cache[key]=gr
   risk[i]=cache[key] if cache[key] is not None else np.nan
  for i in inds:
   r=rows[i];key=r['genome'] if kind=='genome' else r['family'];heapq.heappush(pending,(r['path'][-1]['date'],i,key,r['ret']))
 return risk
def calibrate(raw,floor,cap):
 a=np.asarray(raw,float);med=float(np.nanmedian(a));a=np.where(np.isfinite(a)&(a>0),a,med);inv=1/a
 lo,hi=0.0,1000.0/max(float(np.nanmedian(inv)),1e-12)
 for _ in range(80):
  mid=(lo+hi)/2;mu=float(np.clip(inv*mid,floor,cap).mean())
  if mu>1:hi=mid
  else:lo=mid
 scale=(lo+hi)/2;w=np.clip(inv*scale,floor,cap)
 return w,{'risk_fill_median':med,'inverse_scale':scale,'floor':floor,'cap':cap,'mean_multiplier':float(w.mean())}
def build_policies(rows):
 raw={'inverse_atr_price':np.array([atr_ratio(r) for r in rows]),'inverse_realized_vol20':np.array([prevol(r) for r in rows]),'inverse_genome_downside':causal_downside(rows,'genome'),'inverse_family_downside':causal_downside(rows,'family')}
 names=['equal_weight'];cols=[np.ones(len(rows))];meta=[{'measure':'equal_weight'}];missing={k:int(np.sum(~np.isfinite(v))) for k,v in raw.items()}
 for k,a in raw.items():
  for fl in FLOORS:
   for cp in CAPS:
    w,m=calibrate(a,fl,cp);names.append(f'{k}_floor{fl}_cap{cp}');cols.append(w);meta.append({'measure':k,**m})
 return names,np.column_stack(cols),meta,missing
def build_events(rows):
 dates=sorted({b['date'] for r in rows for b in r['path']});dm={d:i for i,d in enumerate(dates)};D=len(dates);n=len(rows)
 ec=np.zeros(D,np.int32);xc=np.zeros(D,np.int32);uc=np.zeros(D,np.int32)
 for r in rows:
  ec[dm[r['path'][0]['date']]]+=1;xc[dm[r['path'][-1]['date']]]+=1
  for b in r['path']:uc[dm[b['date']]]+=1
 eo=np.r_[0,np.cumsum(ec,dtype=np.int64)];xo=np.r_[0,np.cumsum(xc,dtype=np.int64)];uo=np.r_[0,np.cumsum(uc,dtype=np.int64)]
 ei=np.empty(n,np.int32);xi=np.empty(n,np.int32);ui=np.empty(int(uo[-1]),np.int32);uf=np.empty(int(uo[-1]),float)
 ep=eo[:-1].copy();xp=xo[:-1].copy();up=uo[:-1].copy();lens=np.empty(n,np.int32)
 for i,r in enumerate(rows):
  p=r['path'];lens[i]=len(p);de=dm[p[0]['date']];dx=dm[p[-1]['date']];ei[ep[de]]=i;ep[de]+=1;xi[xp[dx]]=i;xp[dx]+=1;prev=float(r['ep'])
  for b in p:
   d=dm[b['date']];j=up[d];ui[j]=i;uf[j]=float(b['close'])/prev;up[d]+=1;prev=float(b['close'])
 active=0;con=[]
 for d in range(D):
  active+=int(ec[d]);con.append(active);active-=int(xc[d])
 med=float(np.median([x for x in con if x>0]));base=1.0/med
 return dates,(eo,ei),(xo,xi),(uo,ui,uf),lens,{'median_concurrency':med,'max_concurrency':int(max(con)),'base_trade_fraction':base,'days':D}
def metrics(dates,wealth,gross,cash):
 wealth=np.asarray(wealth);dr=np.r_[1.0,wealth[1:]/wealth[:-1]]-1;peak=np.maximum.accumulate(wealth);dd=wealth/peak-1;end=int(np.argmin(dd));start=int(np.argmax(wealth[:end+1])) if end>=0 else 0
 years=max((np.datetime64(dates[-1])-np.datetime64(dates[0])).astype('timedelta64[D]').astype(int)/365.25,1/365.25);term=float(wealth[-1]);cagr=float(term**(1/years)-1) if term>0 else -1.0;q=float(np.quantile(dr,.05));cvar=float(dr[dr<=q].mean())
 return {'terminal_wealth':term,'cagr_equivalent':cagr,'max_drawdown':float(dd.min()),'max_drawdown_start':dates[start],'max_drawdown_trough':dates[end],'daily_p05':q,'daily_cvar05':cvar,'daily_volatility':float(dr.std(ddof=1)),'return_to_drawdown':float((term-1)/abs(dd.min())) if dd.min()<0 else None,'avg_gross_exposure':float(np.mean(gross)),'peak_gross_exposure':float(np.max(gross)),'min_cash_fraction':float(np.min(cash))}
def simulate(dates,entries,exits,updates,W,base,allow_borrow):
 eo,ei=entries;xo,xi=exits;uo,ui,uf=updates;n,P=W.shape;cash=np.ones(P);val=np.zeros((n,P));wealth=[];gross=[];cashfrac=[]
 for d in range(len(dates)):
  prev_eq=cash+val.sum(axis=0);inds=ei[eo[d]:eo[d+1]]
  if len(inds):
   req=base*prev_eq[None,:]*W[inds,:];tot=req.sum(axis=0)
   if not allow_borrow:
    sc=np.minimum(1.0,np.divide(cash,tot,out=np.ones_like(cash),where=tot>0));req*=sc[None,:]
   val[inds,:]=req;cash-=req.sum(axis=0)
  us=ui[uo[d]:uo[d+1]];fac=uf[uo[d]:uo[d+1]]
  if len(us):val[us,:]*=fac[:,None]
  outs=xi[xo[d]:xo[d+1]]
  if len(outs):cash+=val[outs,:].sum(axis=0);val[outs,:]=0.0
  eq=cash+val.sum(axis=0);wealth.append(eq.copy());gross.append(np.divide(val.sum(axis=0),eq,out=np.zeros(P),where=eq!=0));cashfrac.append(np.divide(cash,eq,out=np.zeros(P),where=eq!=0))
 return np.asarray(wealth),np.asarray(gross),np.asarray(cashfrac)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 z,m=load(a.cache,a.manifest);allrows=z['rows'];rows=[r for r in allrows if r['signal_date']<SPLIT]
 names,W,meta,missing=build_policies(rows);dates,entries,exits,updates,lens,ass=build_events(rows)
 wa,ga,ca=simulate(dates,entries,exits,updates,W,ass['base_trade_fraction'],False)
 dur=(W*lens[:,None]).sum(axis=0);scale=dur[0]/dur;Wr=W*scale[None,:]
 wb,gb,cb=simulate(dates,entries,exits,updates,Wr,ass['base_trade_fraction'],True)
 res=[]
 for j,nm in enumerate(names):
  res.append({'name':nm,'calibration':meta[j],'risk_budget_duration_scale':float(scale[j]),'nonlevered':metrics(dates,wa[:,j],ga[:,j],ca[:,j]),'risk_budget':metrics(dates,wb[:,j],gb[:,j],cb[:,j]),'wealth_path_nonlevered':wa[:,j].tolist(),'wealth_path_risk_budget':wb[:,j].tolist()})
 out={'stage':'STAGE1_PORTFOLIO_DEVELOPMENT_ONLY','protocol_sha256':sha(a.protocol),'code_sha256':sha(__file__),'cache_manifest':m,'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in allrows),'split':SPLIT},'holdout_accessed_for_results':False,'verification_a_accessed':False,'verification_b_accessed':False,'missingness':missing,'portfolio_assumptions':{**ass,'entry_sizing_equity':'prior_close_equity','same_day_scarcity':'pro_rata_across_same_day_entries','exit_funding':'close proceeds available next session only','daily_mark':'entry open to close then close-to-close','idle_cash_return':0.0,'risk_budget_note':'diagnostic borrowing allowed; multipliers duration-normalized to baseline scheduled gross exposure'},'dates':dates,'policies':res}
 Path(a.output).write_text(json.dumps(out,sort_keys=True)+'\n')
 print('POLICIES',len(res));print('BASE_A',res[0]['nonlevered']);print('BASE_B',res[0]['risk_budget']);print('OUTPUT',a.output);print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

