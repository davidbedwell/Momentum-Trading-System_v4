#!/usr/bin/env python3
import argparse,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT,prevol,atr_ratio
from run_discovery_portfolio_allocation_architecture import causal_score,grouped,boot,match_equal_exposure,same_day_rank

def causal_day_gates(rows):
    by=defaultdict(list)
    for i,r in enumerate(rows): by[r['signal_date']].append(i)
    past_v=[]; past_a=[]; gates={}
    for d in sorted(by):
        ids=by[d]
        vv=[prevol(rows[i]) for i in ids]; aa=[atr_ratio(rows[i]) for i in ids]
        v=float(np.nanmedian(vv)) if np.isfinite(vv).any() else math.nan
        a=float(np.nanmedian(aa)) if np.isfinite(aa).any() else math.nan
        if len(past_v)>=20 and np.isfinite(v):
            vm=float(np.quantile(past_v,.50)); vq=float(np.quantile(past_v,.75))
        else: vm=vq=math.nan
        if len(past_a)>=20 and np.isfinite(a):
            am=float(np.quantile(past_a,.50)); aq=float(np.quantile(past_a,.75))
        else: am=aq=math.nan
        gates[d]={
          'vol_med':np.isfinite(vm) and v<=vm,'vol_q75':np.isfinite(vq) and v<=vq,
          'atr_med':np.isfinite(am) and a<=am,'atr_q75':np.isfinite(aq) and a<=aq,
          'both_med':np.isfinite(vm) and np.isfinite(am) and v<=vm and a<=am,
          'both_q75':np.isfinite(vq) and np.isfinite(aq) and v<=vq and a<=aq}
        if np.isfinite(v): past_v.append(v)
        if np.isfinite(a): past_a.append(a)
    return gates

def gated_weights(rows,score,gate_map,gate_name,cap):
    s=np.asarray(score,float).copy()
    for i,r in enumerate(rows):
        if not gate_map[r['signal_date']][gate_name]: s[i]=np.nan
    return same_day_rank(rows,s,.50,cap,True)

def main():
    ap=argparse.ArgumentParser()
    for x in ('cache','manifest','protocol','output'): ap.add_argument('--'+x,required=True)
    a=ap.parse_args(); z,m=load(a.cache,a.manifest)
    rows=[r for r in z['rows'] if r['signal_date']<SPLIT]; ret=np.asarray([r['ret'] for r in rows],float)
    score,src=causal_score(rows); gm=causal_day_gates(rows)
    specs=[('equal',np.ones(len(rows)),'control')]
    for g in ('vol_med','vol_q75','atr_med','atr_q75','both_med','both_q75'):
        for cap in (1.25,1.50):
            specs.append((f'riskgate_{g}_budget_top50_c{cap:.2f}',gated_weights(rows,score,gm,g,cap),g))
    W=np.column_stack([x[1] for x in specs]); dates,en,ex,up,lens,ass=build_events(rows)
    wealth,gross,cash=simulate(dates,en,ex,up,W,ass['base_trade_fraction'],False)
    base=metrics(dates,wealth[:,0],gross[:,0],cash[:,0]); out=[]
    for j,(name,w,fam) in enumerate(specs[1:],1):
        d=ret*(w-1); gs={k:grouped(rows,d,k) for k in ('ticker','year','family','genome')}; ci=boot(rows,d)
        pm=metrics(dates,wealth[:,j],gross[:,j],cash[:,j]); embase,em=match_equal_exposure(dates,en,ex,up,len(rows),pm['avg_gross_exposure'])
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
        c['family_caps_passing']=sum(x['pre_neighborhood_pass'] for x in out if x['family']==c['family'])
        c['nominee']=bool(c['pre_neighborhood_pass'] and c['family_caps_passing']==2)
    res={'stage':'RISK_STATE_ALLOCATION_DEVELOPMENT','protocol_sha256':sha(a.protocol),'population':{'development':len(rows),'holdout_reserved':sum(r['signal_date']>=SPLIT for r in z['rows'])},
         'baseline':base,'score_sources':dict(src),'candidate_count':len(out),'nominee_count':sum(x['nominee'] for x in out),
         'holdout_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':out}
    Path(a.output).write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('CANDIDATES',len(out),'NOMINEES',res['nominee_count'])
    for x in sorted(out,key=lambda q:q['portfolio']['terminal_wealth'],reverse=True):
        fail=','.join(k for k,v in x['gate'].items() if not v)
        print(x['name'],'wealth',round(x['portfolio']['terminal_wealth'],6),'rel',round(100*x['wealth_vs_equal_rel'],3),
              'em_rel',round(100*x['wealth_vs_exposure_matched_rel'],3),'DD',round(100*x['portfolio']['max_drawdown'],3),
              'CVaR',round(100*x['portfolio']['daily_cvar05'],4),'fail',fail or 'NONE','nom',x['nominee'])
    print('HOLDOUT_ACCESSED=False VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
