#!/usr/bin/env python3
import argparse,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
SEED=20261002; BOOT=2000; MINN=100; SCALE=3.154602090106647

def causal_score(rows):
    by=defaultdict(list)
    for i,r in enumerate(rows): by[r['signal_date']].append(i)
    gh=defaultdict(list); fh=defaultdict(list); glob=[]; pending=[]
    score=np.full(len(rows),np.nan); src=np.empty(len(rows),object)
    def stat(h):
        a=np.asarray(h,float); ev=float(a.mean()); p10=max(1e-12,-float(np.quantile(a,.10)))
        return max(ev,0.0)/p10
    for d in sorted(by):
        while pending and pending[0][0] < d:
            _,i=heapq.heappop(pending); r=rows[i]; x=float(r['ret'])
            gh[r['genome']].append(x); fh[r['family']].append(x); glob.append(x)
        cache={}
        for i in by[d]:
            r=rows[i]
            if len(gh[r['genome']])>=MINN: key=('genome',r['genome']); h=gh[r['genome']]
            elif len(fh[r['family']])>=MINN: key=('family',r['family']); h=fh[r['family']]
            elif len(glob)>=MINN: key=('global','global'); h=glob
            else: key=('unavailable','x'); h=None
            src[i]=key[0]
            if h is not None:
                if key not in cache: cache[key]=stat(h)
                score[i]=cache[key]
        for i in by[d]: heapq.heappush(pending,(rows[i]['path'][-1]['date'],i))
    return score,Counter(src)

def grouped(rows,d,key):
    s=defaultdict(float)
    for r,x in zip(rows,d): s[r[key]]+=float(x)
    pos=[v for v in s.values() if v>0]; tot=sum(pos)
    return {'groups':len(s),'positive':len(pos),'fraction':len(pos)/len(s) if s else 0.0,
            'max_positive_share':max(pos)/tot if pos and tot>0 else None}

def boot(rows,d):
    tick=sorted(set(r['ticker'] for r in rows)); ix={t:i for i,t in enumerate(tick)}
    s=np.zeros(len(tick)); n=np.zeros(len(tick),int)
    for r,x in zip(rows,d): j=ix[r['ticker']]; s[j]+=x; n[j]+=1
    rng=np.random.default_rng(SEED); out=np.empty(BOOT)
    for b in range(BOOT):
        q=rng.integers(0,len(tick),len(tick)); out[b]=s[q].sum()/n[q].sum()
    return [float(np.quantile(out,.025)),float(np.quantile(out,.975))]

def same_day_rank(rows,score,topfrac,cap,fixed_budget=False):
    w=np.ones(len(rows)); by=defaultdict(list)
    for i,r in enumerate(rows): by[r['signal_date']].append(i)
    for ids in by.values():
        valid=[i for i in ids if np.isfinite(score[i])]
        if not valid: continue
        valid.sort(key=lambda i:score[i],reverse=True)
        k=max(1,int(math.ceil(len(valid)*topfrac))); top=set(valid[:k])
        if fixed_budget and len(valid)>k:
            low=(len(valid)-k*cap)/(len(valid)-k)
            low=max(.50,low)
            for i in valid: w[i]=cap if i in top else low
        else:
            for i in top: w[i]=cap
    return w

def match_equal_exposure(dates,en,ex,up,n,target):
    W=np.ones((n,1)); lo=1e-8; hi=.01
    for _ in range(14):
        mid=(lo+hi)/2; wa,ga,ca=simulate(dates,en,ex,up,W,mid,False)
        x=metrics(dates,wa[:,0],ga[:,0],ca[:,0])['avg_gross_exposure']
        if x<target: lo=mid
        else: hi=mid
    base=(lo+hi)/2; wa,ga,ca=simulate(dates,en,ex,up,W,base,False)
    return base,metrics(dates,wa[:,0],ga[:,0],ca[:,0])

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args()
    z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]
    ret=np.asarray([float(r['ret']) for r in rows])
    score,src=causal_score(rows)
    scaled=np.where(np.isfinite(score),score*SCALE,np.nan)
    specs=[('equal',np.ones(len(rows)),'control')]
    specs.append(('legacy_centered_f0.75_c1.50',np.where(np.isfinite(scaled),np.clip(scaled,.75,1.50),1.0),'legacy'))
    for cap in (1.10,1.25,1.50):
        w=np.where(np.isfinite(scaled),np.clip(scaled,1.0,cap),1.0)
        specs.append((f'boost_only_c{cap:.2f}',w,'boost_only'))
    for q in (.25,.50):
        for cap in (1.10,1.25,1.50):
            specs.append((f'sameday_top{int(q*100)}_c{cap:.2f}',same_day_rank(rows,score,q,cap,False),'sameday_boost'))
            specs.append((f'sameday_budget_top{int(q*100)}_c{cap:.2f}',same_day_rank(rows,score,q,cap,True),'sameday_budget'))
    W=np.column_stack([w for _,w,_ in specs])
    dates,en,ex,up,lens,ass=build_events(rows)
    wealth,gross,cash=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False)
    base=metrics(dates,wealth[:,0],gross[:,0],cash[:,0])
    out=[]
    for j,(name,w,fam) in enumerate(specs[1:],1):
        d=ret*(w-1.0)
        gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}
        ci=boot(rows,d)
        pm=metrics(dates,wealth[:,j],gross[:,j],cash[:,j])
        embase,em=match_equal_exposure(dates,en,ex,up,len(rows),pm['avg_gross_exposure'])
        gate={
          'mean_positive':bool(float(d.mean())>0),
          'ticker60':bool(gs['ticker']['fraction']>=.60),
          'year60':bool(gs['year']['fraction']>=.60),
          'family60':bool(gs['family']['fraction']>=.60),
          'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
          'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
          'cluster_ci_positive':bool(ci[0]>0),
          'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),
          'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))
        }
        out.append({'name':name,'family':fam,'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,
                    'portfolio':pm,'exposure_matched_equal':{'base_trade_fraction':embase,'metrics':em},
                    'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                    'wealth_vs_exposure_matched_rel':float(pm['terminal_wealth']/em['terminal_wealth']-1),
                    'gate':gate,'pre_neighborhood_pass':all(gate.values())})
    for c in out:
        fam=c['family']; c['passing_family_neighbors']=sum(x['pre_neighborhood_pass'] for x in out if x['family']==fam)
        c['nominee']=bool(c['pre_neighborhood_pass'] and c['passing_family_neighbors']>=2)
    res={'stage':'PORTFOLIO_ALLOCATION_ARCHITECTURE_DEVELOPMENT','protocol_sha256':sha(a.protocol),
         'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'score':'causal_ev_over_p10_downside','frozen_scale':SCALE,'score_sources':dict(src),'baseline':base,
         'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('DEVELOPMENT_TRADES',len(rows),'CANDIDATES',len(out),'NOMINEES',res['nominee_count'])
    for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True):
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'rel',round(100*x['wealth_vs_equal_rel'],3),
              'em_rel',round(100*x['wealth_vs_exposure_matched_rel'],3),'mean_d',round(x['mean_delta'],7),
              'T',round(x['groups']['ticker']['fraction'],3),'Y',round(x['groups']['year']['fraction'],3),
              'F',round(x['groups']['family']['fraction'],3),'pass',x['pre_neighborhood_pass'],'nom',x['nominee'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
