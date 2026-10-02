#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot

CAPS=(1.10,1.25,1.50)

def within_group_weights(rows,score,key,cap):
    w=np.ones(len(rows)); by=defaultdict(list)
    for i,r in enumerate(rows): by[(r['path'][0]['date'],r[key])].append(i)
    for ids in by.values():
        valid=[i for i in ids if np.isfinite(score[i])]
        if len(valid)<=1: continue
        valid.sort(key=lambda i:score[i],reverse=True)
        k=max(1,int(math.ceil(len(valid)*.50))); top=set(valid[:k])
        low=(len(valid)-k*cap)/(len(valid)-k)
        if low<0: continue
        for i in valid: w[i]=cap if i in top else low
    return w

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]; ret=np.asarray([r['ret'] for r in rows],float)
    score,src=causal_score(rows); dates,en,ex,up,lens,ass=build_events(rows)
    specs=[('equal',np.ones(len(rows)),'control')]
    for key in ('ticker','family'):
        for cap in CAPS:
            specs.append((f'within_{key}_top50_c{cap:.2f}',within_group_weights(rows,score,key,cap),key))
    W=np.column_stack([x[1] for x in specs]); wealth,gross,cash=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False)
    base=metrics(dates,wealth[:,0],gross[:,0],cash[:,0]); out=[]
    for j,(name,w,fam) in enumerate(specs[1:],1):
        d=ret*(w-1.0); gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        pm=metrics(dates,wealth[:,j],gross[:,j],cash[:,j])
        gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),
              'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),
              'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
              'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
              'cluster_ci_positive':bool(ci[0]>0),'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),
              'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))}
        out.append({'name':name,'family':fam,'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,
                    'portfolio':pm,'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                    'gate':gate,'pre_neighborhood_pass':all(gate.values())})
    for x in out:
        x['passing_family_neighbors']=sum(y['pre_neighborhood_pass'] for y in out if y['family']==x['family'])
        x['nominee']=bool(x['pre_neighborhood_pass'] and x['passing_family_neighbors']>=2)
    res={'stage':'WITHIN_GROUP_RANKING_DEVELOPMENT','protocol_sha256':sha(a.protocol),
         'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'baseline':base,'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('BASE',base)
    for x in out:
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'rel',round(100*x['wealth_vs_equal_rel'],3),
              'DD',round(100*x['portfolio']['max_drawdown'],3),'CVaR',round(100*x['portfolio']['daily_cvar05'],4),
              'T',round(x['groups']['ticker']['fraction'],3),'Y',round(x['groups']['year']['fraction'],3),
              'F',round(x['groups']['family']['fraction'],3),'fail',fail or 'NONE','nom',x['nominee'])
    print('NOMINEES',res['nominee_count'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
