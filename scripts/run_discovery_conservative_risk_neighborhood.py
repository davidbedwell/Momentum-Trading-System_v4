#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot,same_day_rank

CAPS=(1.10,1.20,1.25)
SCALES=(.85,.90,.95)

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]
    ret=np.asarray([r['ret'] for r in rows],float); score,src=causal_score(rows)
    dates,en,ex,up,lens,ass=build_events(rows)
    W0=np.ones((len(rows),1)); wa,ga,ca=simulate(dates,en,ex,up,W0,ass['base_trade_fraction'],False)
    base=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
    eq={}
    for sc in SCALES:
        wa,ga,ca=simulate(dates,en,ex,up,W0,ass['base_trade_fraction']*sc,False)
        eq[sc]=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
    out=[]
    for cap in CAPS:
        w=same_day_rank(rows,score,.50,cap,True); d=ret*(w-1.0)
        gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        trade_gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),
                    'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),
                    'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
                    'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
                    'cluster_ci_positive':bool(ci[0]>0)}
        for sc in SCALES:
            wa,ga,ca=simulate(dates,en,ex,up,w[:,None],ass['base_trade_fraction']*sc,False)
            pm=metrics(dates,wa[:,0],ga[:,0],ca[:,0])
            gate={**trade_gate,'wealth_gt_equal100':bool(pm['terminal_wealth']>base['terminal_wealth']),
                  'wealth_gt_equal_same_risk':bool(pm['terminal_wealth']>eq[sc]['terminal_wealth']),
                  'max_drawdown_no_worse_equal100':bool(pm['max_drawdown']>=base['max_drawdown']),
                  'cvar05_no_worse_equal100':bool(pm['daily_cvar05']>=base['daily_cvar05'])}
            out.append({'name':f'budget_top50_c{cap:.2f}_risk{int(sc*100)}','cap':cap,'risk_scale':sc,
                        'portfolio':pm,'equal_same_risk':eq[sc],
                        'wealth_vs_equal100_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                        'wealth_vs_equal_same_risk_rel':float(pm['terminal_wealth']/eq[sc]['terminal_wealth']-1),
                        'trade_evidence':{'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci},
                        'gate':gate,'pass':all(gate.values())})
    passed=[x for x in out if x['pass']]; pcaps=sorted(set(x['cap'] for x in passed)); psc=sorted(set(x['risk_scale'] for x in passed))
    plateau=len(passed)>=4 and len(pcaps)>=2 and len(psc)>=2
    res={'stage':'CONSERVATIVE_RISK_NORMALIZED_NEIGHBORHOOD','protocol_sha256':sha(a.protocol),
         'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'baseline_equal100':base,'equal_controls':{str(k):v for k,v in eq.items()},
         'passed_count':len(passed),'passed_caps':pcaps,'passed_risk_scales':psc,'plateau_supported':plateau,
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('BASE',base['terminal_wealth'],base['max_drawdown'],base['daily_cvar05'])
    for x in out:
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'vs100',round(100*x['wealth_vs_equal100_rel'],3),
              'DD',round(100*x['portfolio']['max_drawdown'],3),'CVaR',round(100*x['portfolio']['daily_cvar05'],4),
              'PASS',x['pass'],'fail',fail or 'NONE')
    print('PASSED_COUNT',len(passed),'CAPS',pcaps,'SCALES',psc,'PLATEAU_SUPPORTED',plateau)
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
