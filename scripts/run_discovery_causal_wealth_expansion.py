#!/usr/bin/env python3
import argparse,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
SEED=20261002; BOOT=2000; MINN=100; SCALE=3.154602090106647

def causal(rows):
    by=defaultdict(list)
    for i,r in enumerate(rows): by[r['signal_date']].append(i)
    gh=defaultdict(list);fh=defaultdict(list);glob=[];pending=[];score=np.full(len(rows),np.nan);src=np.empty(len(rows),object)
    def calc(h):
        a=np.asarray(h,float); return max(float(a.mean()),0.0)/max(1e-12,-float(np.quantile(a,.10)))
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
                if key not in cache:cache[key]=calc(h)
                score[i]=cache[key]
        for i in by[d]:heapq.heappush(pending,(r['path'][-1]['date'] if False else rows[i]['path'][-1]['date'],i))
    return score,Counter(src)

def groups(rows,d,key):
    s=defaultdict(float)
    for r,x in zip(rows,d):s[r[key]]+=float(x)
    pos=[v for v in s.values() if v>0];tot=sum(pos)
    return {'groups':len(s),'positive':len(pos),'fraction':len(pos)/len(s) if s else 0,'max_positive_share':max(pos)/tot if pos and tot>0 else None}

def boot(rows,d):
    ts=sorted(set(r['ticker'] for r in rows));ix={t:i for i,t in enumerate(ts)};s=np.zeros(len(ts));n=np.zeros(len(ts),int)
    for r,x in zip(rows,d):j=ix[r['ticker']];s[j]+=x;n[j]+=1
    rng=np.random.default_rng(SEED);v=np.empty(BOOT)
    for b in range(BOOT):q=rng.integers(0,len(ts),len(ts));v[b]=s[q].sum()/n[q].sum()
    return [float(np.quantile(v,.025)),float(np.quantile(v,.975))]

def sameday(rows,score,frac,cap,density=False):
    w=np.ones(len(rows));by=defaultdict(list)
    for i,r in enumerate(rows):by[r['signal_date']].append(i)
    for ids in by.values():
        valid=[i for i in ids if np.isfinite(score[i])]
        if not valid:continue
        valid.sort(key=lambda i:score[i],reverse=True);k=max(1,int(math.ceil(len(valid)*frac)));top=valid[:k]
        mult=cap
        if density:
            # simple opportunity-density state: full expansion only when >=4 valid simultaneous opportunities;
            # otherwise halfway from 1x to cap.
            mult=cap if len(valid)>=4 else 1.0+(cap-1.0)*.5
        for i in top:w[i]=mult
    return w

def exposure_match(dates,en,ex,up,n,target):
    W=np.ones((n,1));lo=1e-8;hi=.01
    for _ in range(12):
        mid=(lo+hi)/2;wa,ga,ca=simulate(dates,en,ex,up,W,mid,False);m=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
        if m['avg_gross_exposure']<target:lo=mid
        else:hi=mid
    mid=(lo+hi)/2;wa,ga,ca=simulate(dates,en,ex,up,W,mid,False);return metrics(dates,wa[:,0],ga[:,0],ca[:,0])

def main():
 ap=argparse.ArgumentParser()
 for x in ('cache','manifest','protocol','output'):ap.add_argument('--'+x,required=True)
 a=ap.parse_args();z,m=load(a.cache,a.manifest);rows=[r for r in z['rows'] if r['signal_date']<SPLIT];ret=np.array([r['ret'] for r in rows]);score,src=causal(rows);scaled=score*SCALE
 specs=[('equal',np.ones(len(rows)),'control')]
 for cap in (1.10,1.25,1.50,1.75,2.00):
  specs.append((f'absolute_boost_c{cap:.2f}',np.where(np.isfinite(scaled),np.clip(scaled,1,cap),1),'absolute'))
  for q in (.25,.50):
   specs.append((f'sameday_top{int(q*100)}_c{cap:.2f}',sameday(rows,score,q,cap,False),'relative'))
   specs.append((f'density_top{int(q*100)}_c{cap:.2f}',sameday(rows,score,q,cap,True),'density'))
 W=np.column_stack([x[1] for x in specs]);dates,en,ex,up,lens,ass=build_events(rows);wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False);base=metrics(dates,wa[:,0],ga[:,0],ca[:,0]);out=[]
 for j,(name,w,fam) in enumerate(specs[1:],1):
  d=ret*(w-1);gs={k:groups(rows,d,k) for k in ('ticker','year','family','genome')};ci=boot(rows,d);pm=metrics(dates,wa[:,j],ga[:,j],ca[:,j]);em=exposure_match(dates,en,ex,up,len(rows),pm['avg_gross_exposure'])
  breadth=bool(float(d.mean())>0 and gs['ticker']['fraction']>=.60 and gs['year']['fraction']>=.60 and gs['family']['fraction']>=.60 and (gs['ticker']['max_positive_share'] or 1)<=.15 and (gs['genome']['max_positive_share'] or 1)<=.15 and ci[0]>0)
  out.append({'name':name,'family':fam,'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'portfolio':pm,'exposure_matched_equal':em,'breadth_pass':breadth,'wealth_vs_equal_rel':pm['terminal_wealth']/base['terminal_wealth']-1,'wealth_vs_exposure_matched_rel':pm['terminal_wealth']/em['terminal_wealth']-1})
 # Pareto: maximize wealth, maximize DD (less negative), maximize CVaR (less negative)
 for c in out:
  p=c['portfolio'];c['pareto']=not any((x['portfolio']['terminal_wealth']>=p['terminal_wealth'] and x['portfolio']['max_drawdown']>=p['max_drawdown'] and x['portfolio']['daily_cvar05']>=p['daily_cvar05'] and (x['portfolio']['terminal_wealth']>p['terminal_wealth'] or x['portfolio']['max_drawdown']>p['max_drawdown'] or x['portfolio']['daily_cvar05']>p['daily_cvar05'])) for x in out)
 for c in out:
  c['family_broad_neighbors']=sum(x['breadth_pass'] for x in out if x['family']==c['family']);c['development_frontier_candidate']=bool(c['breadth_pass'] and c['pareto'] and c['family_broad_neighbors']>=3)
 res={'stage':'CAUSAL_WEALTH_EXPANSION_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},'score_sources':dict(src),'baseline':base,'candidate_count':len(out),'frontier_candidate_count':sum(x['development_frontier_candidate'] for x in out),'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
 Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
 print('TRADES',len(rows),'CANDIDATES',len(out),'FRONTIER',res['frontier_candidate_count'])
 for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True):
  p=x['portfolio'];print(x['name'],'W',round(p['terminal_wealth'],4),'rel%',round(100*x['wealth_vs_equal_rel'],2),'EM%',round(100*x['wealth_vs_exposure_matched_rel'],2),'DD%',round(100*p['max_drawdown'],2),'CV%',round(100*p['daily_cvar05'],3),'avgexp',round(p['avg_gross_exposure'],3),'breadth',x['breadth_pass'],'pareto',x['pareto'],'frontier',x['development_frontier_candidate'])
 print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()
