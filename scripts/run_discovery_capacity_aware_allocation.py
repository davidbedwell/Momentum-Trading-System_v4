#!/usr/bin/env python3
import argparse,json,heapq,math
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot,match_equal_exposure,SCALE

def portfolio_state(rows):
    ent=Counter(r['path'][0]['date'] for r in rows)
    ext=Counter(r['path'][-1]['date'] for r in rows)
    dates=sorted(set(ent)|set(ext)); active=0; pre={}; after={}
    daily=[]
    for d in dates:
        pre[d]=active
        active+=ent[d]
        after[d]=active
        daily.append(active)
        active-=ext[d]
    pos=np.asarray([x for x in daily if x>0],float)
    return pre,after,{'median':float(np.median(pos)),'q75':float(np.quantile(pos,.75)),'max':float(np.max(pos))}

def capacity_rank(rows,score,topfrac,cap,pre,threshold=None,fixed_budget=False,headroom=False,ceiling=None):
    w=np.ones(len(rows)); by=defaultdict(list)
    for i,r in enumerate(rows): by[r['path'][0]['date']].append(i)
    for d,ids in by.items():
        valid=[i for i in ids if np.isfinite(score[i])]
        if not valid: continue
        if threshold is not None and pre[d]>threshold: continue
        valid.sort(key=lambda i:score[i],reverse=True)
        k=max(1,int(math.ceil(len(valid)*topfrac))); top=set(valid[:k])
        effcap=cap
        if headroom:
            room=max(0.0,min(1.0,(ceiling-pre[d])/max(ceiling,1.0)))
            effcap=1.0+(cap-1.0)*room
        if fixed_budget and len(valid)>k:
            low=(len(valid)-k*effcap)/(len(valid)-k)
            low=max(.50,low)
            for i in valid: w[i]=effcap if i in top else low
        else:
            for i in top: w[i]=effcap
    return w

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]
    ret=np.asarray([float(r['ret']) for r in rows]); score,src=causal_score(rows)
    pre,after,cs=portfolio_state(rows)
    specs=[('equal',np.ones(len(rows)),'control')]
    for gate_name,threshold in (('median',cs['median']),('q75',cs['q75'])):
        for cap in (1.25,1.50):
            specs.append((f'capboost_{gate_name}_top50_c{cap:.2f}',capacity_rank(rows,score,.50,cap,pre,threshold,False,False,None),'capacity_boost'))
            specs.append((f'capbudget_{gate_name}_top50_c{cap:.2f}',capacity_rank(rows,score,.50,cap,pre,threshold,True,False,None),'capacity_budget'))
    for cap in (1.25,1.50):
        specs.append((f'headroom_top50_c{cap:.2f}',capacity_rank(rows,score,.50,cap,pre,None,False,True,cs['max']),'headroom_boost'))
        specs.append((f'headroom_budget_top50_c{cap:.2f}',capacity_rank(rows,score,.50,cap,pre,None,True,True,cs['max']),'headroom_budget'))
    W=np.column_stack([x[1] for x in specs]); dates,en,ex,up,lens,ass=build_events(rows)
    wealth,gross,cash=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False)
    base=metrics(dates,wealth[:,0],gross[:,0],cash[:,0]); out=[]
    for j,(name,w,fam) in enumerate(specs[1:],1):
        d=ret*(w-1.0); gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        pm=metrics(dates,wealth[:,j],gross[:,j],cash[:,j])
        embase,em=match_equal_exposure(dates,en,ex,up,len(rows),pm['avg_gross_exposure'])
        gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),'year60':bool(gs['year']['fraction']>=.60),
              'family60':bool(gs['family']['fraction']>=.60),'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
              'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),'cluster_ci_positive':bool(ci[0]>0),
              'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),
              'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))}
        out.append({'name':name,'family':fam,'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'portfolio':pm,
                    'exposure_matched_equal':{'base_trade_fraction':embase,'metrics':em},
                    'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                    'wealth_vs_exposure_matched_rel':float(pm['terminal_wealth']/em['terminal_wealth']-1),
                    'gate':gate,'pre_neighborhood_pass':all(gate.values())})
    for c in out:
        c['passing_family_neighbors']=sum(x['pre_neighborhood_pass'] for x in out if x['family']==c['family'])
        c['nominee']=bool(c['pre_neighborhood_pass'] and c['passing_family_neighbors']>=2)
    res={'stage':'CAPACITY_AWARE_ALLOCATION_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'concurrency':cs,'score_sources':dict(src),'baseline':base,'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('CONCURRENCY',cs,'CANDIDATES',len(out),'NOMINEES',res['nominee_count'])
    for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True):
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'rel',round(x['wealth_vs_equal_rel']*100,3),
              'em_rel',round(x['wealth_vs_exposure_matched_rel']*100,3),'DD',round(x['portfolio']['max_drawdown']*100,3),
              'CVaR',round(x['portfolio']['daily_cvar05']*100,4),'T',round(x['groups']['ticker']['fraction'],3),
              'fail',fail or 'NONE','nom',x['nominee'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
