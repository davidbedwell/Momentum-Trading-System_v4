#!/usr/bin/env python3
import argparse,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
SEED=20261002;BOOT=2000;MINN=100;SCALE=3.154602090106647
CAPS=(2.25,2.50,3.00,3.50,4.00)

def causal(rows):
 by=defaultdict(list)
 for i,r in enumerate(rows):by[r['signal_date']].append(i)
 gh=defaultdict(list);fh=defaultdict(list);glob=[];pending=[];s=np.full(len(rows),np.nan);src=np.empty(len(rows),object)
 def stat(h):
  a=np.asarray(h,float);return max(float(a.mean()),0)/max(1e-12,-float(np.quantile(a,.10)))
 for d in sorted(by):
  while pending and pending[0][0]<d:
   _,i=heapq.heappop(pending);r=rows[i];x=float(r['ret']);gh[r['genome']].append(x);fh[r['family']].append(x);glob.append(x)
  cache={}
  for i in by[d]:
   r=rows[i]
   if len(gh[r['genome']])>=MINN:key=('genome',r['genome']);h=gh[r['genome']]
   elif len(fh[r['family']])>=MINN:key=('family',r['family']);h=fh[r['family']]
   elif len(glob)>=MINN:key=('global','global');h=glob
   else:key=('unavailable','x');h=None
   src[i]=key[0]
   if h is not None:
    if key not in cache:cache[key]=stat(h)
    s[i]=cache[key]
  for i in by[d]:heapq.heappush(pending,(rows[i]['path'][-1]['date'],i))
 return s,Counter(src)

def sameday(rows,score,q,cap):
 w=np.ones(len(rows));by=defaultdict(list)
 for i,r in enumerate(rows):by[r['signal_date']].append(i)
 for ids in by.values():
  v=[i for i in ids if np.isfinite(score[i])]
  if not v:continue
  v.sort(key=lambda i:score[i],reverse=True);k=max(1,int(math.ceil(len(v)*q)))
  for i in v[:k]:w[i]=cap
 return w

def groups(rows,d,key):
 s=defaultdict(float)
 for r,x in zip(rows,d):s[r[key]]+=float(x)
 pos=[v for v in s.values() if v>0];tot=sum(pos)
 return {'groups':len(s),'positive':len(pos),'fraction':len(pos)/len(s) if s else 0,'max_positive_share':max(pos)/tot if pos and tot>0 else None}
def boot(rows,d):
 tick=sorted(set(r['ticker'] for r in rows));ix={t:i for i,t in enumerate(tick)};s=np.zeros(len(tick));n=np.zeros(len(tick),int)
 for r,x in zip(rows,d):j=ix[r['ticker']];s[j]+=x;n[j]+=1
 rng=np.random.default_rng(SEED);v=np.empty(BOOT)
 for b in range(BOOT):q=rng.integers(0,len(tick),len(tick));v[b]=s[q].sum()/n[q].sum()
 return [float(np.quantile(v,.025)),float(np.quantile(v,.975))]
def matched(dates,en,ex,up,n,target):
 W=np.ones((n,1));lo=1e-8;hi=.01
 for _ in range(14):
  mid=(lo+hi)/2;wa,ga,ca=simulate(dates,en,ex,up,W,mid,False);x=metrics(dates,wa[:,0],ga[:,0],ca[:,0])['avg_gross_exposure']
  if x<target:lo=mid
  else:hi=mid
 b=(lo+hi)/2;wa,ga,ca=simulate(dates,en,ex,up,W,b,False);return b,metrics(dates,wa[:,0],ga[:,0],ca[:,0])
def main():
 ap=argparse.ArgumentParser()
 for x in ('cache','manifest','protocol','output'):ap.add_argument('--'+x,required=True)
 a=ap.parse_args();z,m=load(a.cache,a.manifest);rows=[r for r in z['rows'] if r['signal_date']<SPLIT];ret=np.array([r['ret'] for r in rows]);score,src=causal(rows);scaled=score*SCALE
 specs=[('equal',np.ones(len(rows)),'equal')]
 for cp in CAPS:specs.append((f'boost_all_c{cp:.2f}',np.where(np.isfinite(scaled),np.clip(scaled,1,cp),1),'boost_all'))
 for q in (.25,.50):
  for cp in CAPS:specs.append((f'sameday_top{int(q*100)}_c{cp:.2f}',sameday(rows,score,q,cp),f'sameday_top{int(q*100)}'))
 W=np.column_stack([x[1] for x in specs]);dates,en,ex,up,lens,ass=build_events(rows);wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False);base=metrics(dates,wa[:,0],ga[:,0],ca[:,0]);out=[]
 for j,(nm,w,fam) in enumerate(specs[1:],1):
  d=ret*(w-1);g={k:groups(rows,d,k) for k in ('ticker','year','family','genome')};ci=boot(rows,d);pm=metrics(dates,wa[:,j],ga[:,j],ca[:,j]);eb,em=matched(dates,en,ex,up,len(rows),pm['avg_gross_exposure'])
  addexp=pm['avg_gross_exposure']-base['avg_gross_exposure'];ddw=max(0,base['max_drawdown']-pm['max_drawdown']);cg=pm['cagr_equivalent']-base['cagr_equivalent']
  broad=bool(d.mean()>0 and g['ticker']['fraction']>=.6 and g['year']['fraction']>=.6 and g['family']['fraction']>=.6 and ci[0]>0 and (g['ticker']['max_positive_share'] or 1)<=.15 and (g['genome']['max_positive_share'] or 1)<=.15)
  out.append({'name':nm,'family':fam,'mean_delta':float(d.mean()),'groups':g,'ticker_cluster_ci95':ci,'portfolio':pm,'exposure_matched_equal':{'base_trade_fraction':eb,'metrics':em},'broad_gate':broad,'wealth_gain_rel':pm['terminal_wealth']/base['terminal_wealth']-1,'wealth_vs_exposure_matched_rel':pm['terminal_wealth']/em['terminal_wealth']-1,'cagr_gain':cg,'maxdd_delta_pp':100*(pm['max_drawdown']-base['max_drawdown']),'cvar_delta_pp':100*(pm['daily_cvar05']-base['daily_cvar05']),'additional_avg_exposure':addexp,'wealth_gain_per_avg_exposure_point':(pm['terminal_wealth']/base['terminal_wealth']-1)/addexp if addexp>0 else None,'cagr_gain_per_additional_maxdd_point':cg/(100*ddw) if ddw>0 else None})
 # nondominated among broad candidates: wealth max, DD and CVaR no worse
 for x in out:
  x['frontier']=x['broad_gate'] and not any(y['broad_gate'] and y['portfolio']['terminal_wealth']>=x['portfolio']['terminal_wealth'] and y['portfolio']['max_drawdown']>=x['portfolio']['max_drawdown'] and y['portfolio']['daily_cvar05']>=x['portfolio']['daily_cvar05'] and (y['portfolio']['terminal_wealth']>x['portfolio']['terminal_wealth'] or y['portfolio']['max_drawdown']>x['portfolio']['max_drawdown'] or y['portfolio']['daily_cvar05']>x['portfolio']['daily_cvar05']) for y in out)
 res={'stage':'CAUSAL_WEALTH_GROWTH_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},'score_sources':dict(src),'baseline':base,'candidate_count':len(out),'frontier_count':sum(x['frontier'] for x in out),'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out};Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
 print('TRADES',len(rows),'CANDIDATES',len(out),'FRONTIER',res['frontier_count'])
 for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True):print(x['name'],'W',round(x['portfolio']['terminal_wealth'],4),'gain%',round(100*x['wealth_gain_rel'],2),'EM%',round(100*x['wealth_vs_exposure_matched_rel'],2),'DDpp',round(x['maxdd_delta_pp'],3),'CVpp',round(x['cvar_delta_pp'],3),'exp',round(x['portfolio']['avg_gross_exposure'],3),'broad',x['broad_gate'],'frontier',x['frontier'])
 print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()
