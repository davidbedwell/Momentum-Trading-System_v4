#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot,same_day_rank

CAPS=(1.20,1.25,1.50)
GUARDS={
 'mild':((-.05,.95),(-.10,.90)),
 'moderate':((-.10,.95),(-.20,.90)),
 'strong':((-.05,.90),(-.10,.80))
}

def risk_scale(dd,tiers):
    sc=1.0
    for threshold,val in tiers:
        if dd<=threshold: sc=val
    return sc

def simulate_guard(dates,entries,exits,updates,w,base,tiers):
    eo,ei=entries; xo,xi=exits; uo,ui,uf=updates
    n=len(w); cash=1.0; val=np.zeros(n,float); peak=1.0
    wealth=[]; gross=[]; cashfrac=[]
    for d in range(len(dates)):
        prev_eq=cash+val.sum()
        dd=prev_eq/peak-1.0
        sc=risk_scale(dd,tiers)
        inds=ei[eo[d]:eo[d+1]]
        if len(inds):
            req=base*sc*prev_eq*w[inds]
            tot=float(req.sum())
            if tot>cash and tot>0: req*=cash/tot
            val[inds]=req; cash-=float(req.sum())
        us=ui[uo[d]:uo[d+1]]; fac=uf[uo[d]:uo[d+1]]
        if len(us): val[us]*=fac
        outs=xi[xo[d]:xo[d+1]]
        if len(outs): cash+=float(val[outs].sum()); val[outs]=0.0
        eq=cash+val.sum(); peak=max(peak,eq)
        wealth.append(eq); gross.append(val.sum()/eq if eq else 0.0); cashfrac.append(cash/eq if eq else 0.0)
    return np.asarray(wealth),np.asarray(gross),np.asarray(cashfrac)

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]; ret=np.asarray([r['ret'] for r in rows],float)
    score,src=causal_score(rows); dates,en,ex,up,lens,ass=build_events(rows); ones=np.ones(len(rows))
    w0,g0,c0=simulate_guard(dates,en,ex,up,ones,ass['base_trade_fraction'],())
    base=metrics(dates,w0,g0,c0)
    equal_guard={}
    for gn,tiers in GUARDS.items():
        w,g,c=simulate_guard(dates,en,ex,up,ones,ass['base_trade_fraction'],tiers)
        equal_guard[gn]=metrics(dates,w,g,c)
    out=[]
    for cap in CAPS:
        ww=same_day_rank(rows,score,.50,cap,True); d=ret*(ww-1)
        gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        tg={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),
            'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),
            'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
            'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
            'cluster_ci_positive':bool(ci[0]>0)}
        for gn,tiers in GUARDS.items():
            w,g,c=simulate_guard(dates,en,ex,up,ww,ass['base_trade_fraction'],tiers); pm=metrics(dates,w,g,c)
            gate={**tg,'wealth_gt_equal100':bool(pm['terminal_wealth']>base['terminal_wealth']),
                  'wealth_gt_equal_same_guard':bool(pm['terminal_wealth']>equal_guard[gn]['terminal_wealth']),
                  'max_drawdown_no_worse_equal100':bool(pm['max_drawdown']>=base['max_drawdown']),
                  'cvar05_no_worse_equal100':bool(pm['daily_cvar05']>=base['daily_cvar05'])}
            out.append({'name':f'budget_top50_c{cap:.2f}_guard_{gn}','cap':cap,'guard':gn,'portfolio':pm,
                        'equal_same_guard':equal_guard[gn],
                        'wealth_vs_equal100_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
                        'wealth_vs_equal_same_guard_rel':float(pm['terminal_wealth']/equal_guard[gn]['terminal_wealth']-1),
                        'trade_evidence':{'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci},
                        'gate':gate,'pass':all(gate.values())})
    passed=[x for x in out if x['pass']]; pc=sorted(set(x['cap'] for x in passed)); pg=sorted(set(x['guard'] for x in passed))
    plateau=len(passed)>=4 and len(pc)>=2 and len(pg)>=2
    res={'stage':'DRAWDOWN_AWARE_RANKING_DEVELOPMENT','protocol_sha256':sha(a.protocol),
         'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'baseline_equal100':base,'equal_guard_controls':equal_guard,'passed_count':len(passed),'passed_caps':pc,'passed_guards':pg,
         'plateau_supported':plateau,'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('BASE',base)
    for x in out:
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'vs100',round(100*x['wealth_vs_equal100_rel'],3),
              'DD',round(100*x['portfolio']['max_drawdown'],3),'CVaR',round(100*x['portfolio']['daily_cvar05'],4),
              'PASS',x['pass'],'fail',fail or 'NONE')
    print('PASSED',len(passed),'CAPS',pc,'GUARDS',pg,'PLATEAU',plateau)
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
