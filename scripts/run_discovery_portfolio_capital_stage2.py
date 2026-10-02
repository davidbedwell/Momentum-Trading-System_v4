#!/usr/bin/env python3
import argparse,gzip,pickle,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,calibrate,SPLIT,FLOORS,CAPS
MINN=100
RISK_STATS=('downside_dev','p10_loss','p05_loss','mae_tail','volatility')
def stat(hist):
 if len(hist)<MINN:return None
 a=np.asarray([x[0] for x in hist],float);mae=np.asarray([x[1] for x in hist],float);neg=np.minimum(a,0.0)
 return {'downside_dev':float(np.sqrt(np.mean(neg*neg))),
         'p10_loss':max(1e-12,-float(np.quantile(a,.10))),
         'p05_loss':max(1e-12,-float(np.quantile(a,.05))),
         'mae_tail':max(1e-12,-float(np.quantile(mae,.10))),
         'volatility':max(1e-12,float(a.std(ddof=1))),
         'expectancy':float(a.mean())}
def causal_hierarchy(rows):
 bydate=defaultdict(list)
 for i,r in enumerate(rows):bydate[r['signal_date']].append(i)
 gh=defaultdict(list);fh=defaultdict(list);glob=[];pending=[]
 out={k:np.full(len(rows),np.nan) for k in RISK_STATS};ev=np.full(len(rows),np.nan);src=np.empty(len(rows),object)
 for d in sorted(bydate):
  while pending and pending[0][0] < d:
   _,i=heapq.heappop(pending);r=rows[i];x=(float(r['ret']),float(r['mae']));gh[r['genome']].append(x);fh[r['family']].append(x);glob.append(x)
  inds=bydate[d];cache={}
  for i in inds:
   r=rows[i]
   if len(gh[r['genome']])>=MINN:key=('genome',r['genome']);h=gh[r['genome']]
   elif len(fh[r['family']])>=MINN:key=('family',r['family']);h=fh[r['family']]
   elif len(glob)>=MINN:key=('global','global');h=glob
   else:key=('unavailable','unavailable');h=None
   if key not in cache:cache[key]=stat(h) if h is not None else None
   q=cache[key];src[i]=key[0]
   if q is not None:
    ev[i]=q['expectancy']
    for k in RISK_STATS:out[k][i]=q[k]
  for i in inds:heapq.heappush(pending,(rows[i]['path'][-1]['date'],i))
 return out,ev,Counter(src)
def calibrate_score(score,floor,cap):
 a=np.asarray(score,float);mask=np.isfinite(a);raw=np.zeros(len(a),float);raw[mask]=np.maximum(a[mask],0.0)
 pos=raw[mask & (raw>0)];base=float(np.nanmedian(pos)) if len(pos) else 1.0;lo,hi=0.0,1000.0/max(base,1e-12)
 for _ in range(80):
  mid=(lo+hi)/2;w=np.ones(len(a),float);w[mask]=np.clip(raw[mask]*mid,floor,cap)
  if float(w.mean())>1:hi=mid
  else:lo=mid
 scale=(lo+hi)/2;w=np.ones(len(a),float);w[mask]=np.clip(raw[mask]*scale,floor,cap)
 return w,{'missing_policy':'neutral_1.0','score_scale':scale,'floor':floor,'cap':cap,'mean_multiplier':float(w.mean())}
def trade_metrics(rows,w):
 r=np.asarray([x['ret'] for x in rows],float)*w;q=np.quantile(r,.05);eq=np.cumsum(r);peak=np.maximum.accumulate(np.r_[0,eq])[1:]
 return {'mean':float(r.mean()),'p05':float(q),'cvar05':float(r[r<=q].mean()),'total_return_units':float(r.sum()),'max_drawdown_return_units':float((eq-peak).min())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 z,m=load(a.cache,a.manifest);allrows=z['rows'];rows=[r for r in allrows if r['signal_date']<SPLIT]
 risks,ev,sources=causal_hierarchy(rows);names=['equal_weight'];cols=[np.ones(len(rows))];meta=[{'mode':'equal_weight'}]
 for rk in RISK_STATS:
  for mode in ('inverse_risk','ev_over_risk'):
   raw=risks[rk] if mode=='inverse_risk' else np.divide(np.maximum(ev,0),risks[rk],out=np.full(len(rows),np.nan),where=np.isfinite(risks[rk])&(risks[rk]>0)&np.isfinite(ev))
   for fl in FLOORS:
    for cp in CAPS:
     if mode=='inverse_risk':w,mm=calibrate(raw,fl,cp)
     else:w,mm=calibrate_score(raw,fl,cp)
     names.append(f'{mode}_{rk}_floor{fl}_cap{cp}');cols.append(w);meta.append({'mode':mode,'risk_stat':rk,**mm})
 W=np.column_stack(cols);dates,entries,exits,updates,lens,ass=build_events(rows)
 wa,ga,ca=simulate(dates,entries,exits,updates,W,ass['base_trade_fraction'],False)
 dur=(W*lens[:,None]).sum(axis=0);sc=dur[0]/dur;Wr=W*sc[None,:];wb,gb,cb=simulate(dates,entries,exits,updates,Wr,ass['base_trade_fraction'],True)
 policies=[]
 for j,nm in enumerate(names):
  policies.append({'name':nm,'calibration':meta[j],'trade_metrics':trade_metrics(rows,W[:,j]),'risk_budget_duration_scale':float(sc[j]),'nonlevered':metrics(dates,wa[:,j],ga[:,j],ca[:,j]),'risk_budget':metrics(dates,wb[:,j],gb[:,j],cb[:,j])})
 out={'stage':'STAGE2_GENOME_FAMILY_DEVELOPMENT_ONLY','protocol_sha256':sha(a.protocol),'code_sha256':sha(__file__),'cache_manifest':m,'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in allrows),'split':SPLIT},'source_counts':dict(sources),'holdout_accessed_for_results':False,'verification_a_accessed':False,'verification_b_accessed':False,'portfolio_assumptions':ass,'candidate_count':len(policies)-1,'policies':policies}
 Path(a.output).write_text(json.dumps(out,sort_keys=True)+'\n');print('STAGE2_CANDIDATES',len(policies)-1);print('SOURCE_COUNTS',dict(sources));print('OUTPUT',a.output);print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

