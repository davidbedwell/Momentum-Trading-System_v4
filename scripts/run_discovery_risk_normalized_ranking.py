#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot,same_day_rank

SCALES=(1.00,.95,.90)
CAPS=(1.25,1.50)

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]
    ret=np.asarray([r['ret'] for r in rows],float)
    score,src=causal_score(rows)
    weights={cap:same_day_rank(rows,score,.50,cap,True) for cap in CAPS}
    contrib={}
    for cap,w in weights.items():
        d=ret*(w-1.0)
        gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}
        ci=boot(rows,d)
        tradegate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),
                   'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),
                   'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
                   'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
                   'cluster_ci_positive':bool(ci[0]>0)}
        contrib[cap]={'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'trade_gate':tradegate}
    dates,en,ex,up,lens,ass=build_events(rows)
    eq={}
    for sc in SCALES:
        W=np.ones((len(rows),1)); wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction']*sc,False)
        eq[sc]=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
    base=eq[1.00]; out=[]
    for cap in CAPS:
        for sc in SCALES:
            W=weights[cap][:,None]
            wa,ga,ca=simulate(dates,en,ex,up,W,ass['base_trade_fraction']*sc,False)
            pm=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
            gate={**contrib[cap]['trade_gate'],
                  'wealth_gt_equal100':bool(pm['terminal_wealth']>base['terminal_wealth']),
                  'wealth_gt_equal_same_risk':bool(pm['terminal_wealth']>eq[sc]['terminal_wealth']),
                  'max_drawdown_no_worse_equal100':bool(pm['max_drawdown']>=base['max_drawdown']),
                  'cvar05_no_worse_equal100':bool(pm['daily_cvar05']>=base['daily_cvar05'])}
            out.append({'name':f'sameday_budget_top50_c{cap:.2f}_risk{int(sc*100)}',
                        'cap':cap,'risk_scale':sc,'portfolio':pm,'equal_same_risk':eq[sc],
                        'wealth_vs_equal100_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                        'wealth_vs_equal_same_risk_rel':float(pm['terminal_wealth']/eq[sc]['terminal_wealth']-1),
                        'trade_evidence':contrib[cap],'gate':gate,'pass':all(gate.values())})
    for x in out:
        x['neighbor_count']=sum(y['pass'] for y in out if y['cap']==x['cap'])
        x['nominee']=bool(x['pass'] and x['neighbor_count']>=2)
    res={'stage':'RISK_NORMALIZED_RANKING_DEVELOPMENT','protocol_sha256':sha(a.protocol),
         'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'base_trade_fraction':ass['base_trade_fraction'],'equal_controls':{str(k):v for k,v in eq.items()},
         'baseline_equal100':base,'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('BASE',base)
    for x in out:
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),
              'vsEq100',round(100*x['wealth_vs_equal100_rel'],3),
              'vsEqRisk',round(100*x['wealth_vs_equal_same_risk_rel'],3),
              'DD',round(100*x['portfolio']['max_drawdown'],3),
              'CVaR',round(100*x['portfolio']['daily_cvar05'],4),
              'fail',fail or 'NONE','nom',x['nominee'])
    print('NOMINEES',res['nominee_count'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
