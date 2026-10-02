#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,metrics,SPLIT
from run_discovery_general_winner_rule_holdout import causal_all,groups,boot
from run_discovery_portfolio_allocation_architecture import same_day_rank,match_equal_exposure
from run_discovery_risk_budgeted_allocation import simulate_budget

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','nominees','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest); rows=z['rows']; nom=json.load(open(a.nominees))
    if nom.get('holdout_accessed') or len(nom.get('nominees',[]))!=2: raise RuntimeError('frozen nominee manifest violation')
    ev,wr,p10,src=causal_all(rows); score=np.maximum(ev,0)/p10
    mask=np.array([r['signal_date']>=SPLIT for r in rows]); hold=[r for r,x in zip(rows,mask) if x]; hs=score[mask]
    dates,E,X,U,lens,ass=build_events(hold); n=len(hold); ret=np.asarray([r['ret'] for r in hold])
    W0=np.ones((n,1)); w0,g0,c0,_=simulate_budget(dates,E,X,U,W0,ass['base_trade_fraction'])
    base=metrics(dates,w0[:,0],g0[:,0],c0[:,0]); results=[]
    for q in nom['nominees']:
        raw=same_day_rank(hold,hs,float(q['top_fraction']),float(q['redistribution_cap']),True)
        wa,ga,ca,bind=simulate_budget(dates,E,X,U,raw[:,None],ass['base_trade_fraction'],float(nom['gross_ceiling']),None)
        pm=metrics(dates,wa[:,0],ga[:,0],ca[:,0]); embase,em=match_equal_exposure(dates,E,X,U,n,pm['avg_gross_exposure'])
        d=ret*(raw-1); gs={k:groups(hold,d,k) for k in ('ticker','year','family','genome')}; ci=boot(hold,d)
        gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),'cluster_ci_positive':bool(ci[0]>0),'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))}
        results.append({'name':q['name'],'top_fraction':q['top_fraction'],'redistribution_cap':q['redistribution_cap'],'gross_ceiling':nom['gross_ceiling'],'binding_day_fraction':float(bind[0]),'mean_delta_scheduled':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'portfolio':pm,'exposure_matched_equal':{'base_trade_fraction':embase,'metrics':em},'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),'wealth_vs_exposure_matched_rel':float(pm['terminal_wealth']/em['terminal_wealth']-1),'gates':gate,'pass':all(gate.values())})
    out={'stage':'RISK_BUDGETED_ALLOCATION_DISCOVERY_HOLDOUT_ONCE','protocol_sha256':sha(a.protocol),'nominee_manifest_sha256':sha(a.nominees),'population':{'holdout':n,'tickers':len(set(r['ticker'] for r in hold))},'baseline':base,'holdout_score_sources':dict(Counter(src[mask])),'results':results,'holdout_replayed_once':True,'verification_a_accessed':False,'verification_b_accessed':False}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print('BASE',base)
    for x in results: print(x['name'],'PASS',x['pass'],'wealth',x['portfolio']['terminal_wealth'],'rel%',100*x['wealth_vs_equal_rel'],'em%',100*x['wealth_vs_exposure_matched_rel'],'DD',x['portfolio']['max_drawdown'],'CV',x['portfolio']['daily_cvar05'],'T/Y/F',x['groups']['ticker']['positive'],x['groups']['year']['positive'],x['groups']['family']['positive'],'CI',x['ticker_cluster_ci95'],'bind',x['binding_day_fraction'],'GATES',x['gates'])
    print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
