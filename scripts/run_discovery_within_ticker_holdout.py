#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot
from run_discovery_within_group_ranking import within_group_weights

EXPECTED_FREEZE='7fdbe9ac1ea1df1e239913277b8a99bfda19a83545981eaee91bb3956a1f7dad'

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','freeze','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args()
    if sha(a.freeze)!=EXPECTED_FREEZE: raise RuntimeError('frozen nominee hash mismatch')
    z,m=load(a.cache,a.manifest); allrows=z['rows']
    score,src=causal_score(allrows)
    wall=within_group_weights(allrows,score,'ticker',1.10)
    idx=[i for i,r in enumerate(allrows) if r['signal_date']>=SPLIT]
    rows=[allrows[i] for i in idx]; w=np.asarray([wall[i] for i in idx],float)
    ret=np.asarray([r['ret'] for r in rows],float); d=ret*(w-1.0)
    dates,en,ex,up,lens,ass=build_events(rows)
    W=np.column_stack([np.ones(len(rows)),w]); wealth,gross,cash=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False)
    base=metrics(dates,wealth[:,0],gross[:,0],cash[:,0]); pm=metrics(dates,wealth[:,1],gross[:,1],cash[:,1])
    gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
    gate={'mean_positive':bool(d.mean()>0),'ticker60':bool(gs['ticker']['fraction']>=.60),
          'year60':bool(gs['year']['fraction']>=.60),'family60':bool(gs['family']['fraction']>=.60),
          'ticker_conc15':bool((gs['ticker']['max_positive_share'] or 1)<=.15),
          'genome_conc15':bool((gs['genome']['max_positive_share'] or 1)<=.15),
          'cluster_ci_positive':bool(ci[0]>0),'wealth_gt_equal':bool(pm['terminal_wealth']>base['terminal_wealth']),
          'not_both_tail_worse':bool(not(pm['max_drawdown']<base['max_drawdown'] and pm['daily_cvar05']<base['daily_cvar05']))}
    out={'stage':'WITHIN_TICKER_RANKING_DISCOVERY_HOLDOUT','freeze_sha256':sha(a.freeze),
         'candidate':'within_ticker_top50_c1.10','population':{'holdout_trades':len(rows),'tickers':len(set(r['ticker'] for r in rows)),
         'start':min(r['signal_date'] for r in rows),'end':max(r['signal_date'] for r in rows)},
         'baseline':base,'candidate_portfolio':pm,'wealth_vs_equal_rel':float(pm['terminal_wealth']/base['terminal_wealth']-1),
         'mean_delta':float(d.mean()),'groups':gs,'ticker_cluster_ci95':ci,'gate':gate,'replicated':all(gate.values()),
         'holdout_note':'Existing Discovery Holdout reused after prior hypotheses; nominee frozen before this architecture replay.',
         'verification_a_accessed':False,'verification_b_accessed':False}
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('HOLDOUT_TRADES',len(rows),'TICKERS',out['population']['tickers'])
    print('BASE',base)
    print('CANDIDATE',pm)
    print('WEALTH_REL',out['wealth_vs_equal_rel'],'MEAN_DELTA',out['mean_delta'])
    print('GROUPS',gs)
    print('CI95',ci)
    print('GATE',gate)
    print('REPLICATED',out['replicated'])
    print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
