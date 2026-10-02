#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from collections import defaultdict
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,atr_ratio,prevol,calibrate,SPLIT
from run_discovery_portfolio_capital_stage2 import causal_hierarchy,calibrate_score
SEED=20261001; BOOT=2000
def group_stats(rows,delta,key):
 sums=defaultdict(float)
 for r,d in zip(rows,delta):sums[r[key]]+=float(d)
 pos={k:v for k,v in sums.items() if v>0};tot=sum(pos.values())
 return {'groups':len(sums),'positive_groups':len(pos),'max_positive_contribution_share':max(pos.values())/tot if tot>0 and pos else None,'sums':dict(sums)}
def ticker_boot(rows,delta):
 tick=sorted(set(r['ticker'] for r in rows));ix={t:i for i,t in enumerate(tick)};s=np.zeros(len(tick));n=np.zeros(len(tick),int)
 for r,d in zip(rows,delta):j=ix[r['ticker']];s[j]+=d;n[j]+=1
 rng=np.random.default_rng(SEED);vals=np.empty(BOOT)
 for b in range(BOOT):
  q=rng.integers(0,len(tick),len(tick));vals[b]=s[q].sum()/n[q].sum()
 return {'replicates':BOOT,'seed':SEED,'mean_delta_ci95':[float(np.quantile(vals,.025)),float(np.quantile(vals,.975))],'median':float(np.median(vals)),'probability_delta_gt_0':float(np.mean(vals>0))}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();z,m=load(a.cache,a.manifest);rows=[r for r in z['rows'] if r['signal_date']<SPLIT];ret=np.asarray([r['ret'] for r in rows],float)
 atr=np.asarray([atr_ratio(r) for r in rows]);vol=np.asarray([prevol(r) for r in rows]);risks,ev,src=causal_hierarchy(rows)
 specs=[];w,_=calibrate(vol,.5,2.0);specs.append(('S1_GROWTH_REALVOL_05_20',w));w,_=calibrate(atr,.5,2.0);specs.append(('S1_GROWTH_ATR_05_20',w));w,_=calibrate(atr,.25,2.0);specs.append(('S1_DRAWDOWN_ATR_025_20',w))
 score=np.divide(np.maximum(ev,0),risks['p10_loss'],out=np.full(len(rows),np.nan),where=np.isfinite(ev)&np.isfinite(risks['p10_loss'])&(risks['p10_loss']>0))
 w,_=calibrate_score(score,.5,2.0);specs.append(('S2_GROWTH_EV_P10_05_20',w));w,_=calibrate_score(score,.25,2.0);specs.append(('S2_DRAWDOWN_EV_P10_025_20',w))
 out={'stage':'DEVELOPMENT_BREADTH_CLUSTER_UNCERTAINTY','protocol_sha256':sha(a.protocol),'candidate_count':len(specs),'holdout_accessed_for_results':False,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':[]}
 for name,w in specs:
  delta=ret*(w-1);c={'name':name,'mean_trade_delta':float(delta.mean()),'total_return_unit_delta':float(delta.sum()),'ticker':group_stats(rows,delta,'ticker'),'year':group_stats(rows,delta,'year'),'family':group_stats(rows,delta,'family'),'genome':group_stats(rows,delta,'genome'),'ticker_cluster_bootstrap':ticker_boot(rows,delta)}
  c['breadth_gate']={'ticker_ge20':c['ticker']['positive_groups']>=20,'year_ge5':c['year']['positive_groups']>=5,'family_ge4':c['family']['positive_groups']>=4,'max_ticker_le20pct':(c['ticker']['max_positive_contribution_share'] or 1)<=.20,'max_genome_le20pct':(c['genome']['max_positive_contribution_share'] or 1)<=.20}
  c['breadth_pass']=all(c['breadth_gate'].values());out['candidates'].append(c)
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 for c in out['candidates']:print(c['name'],'delta',c['mean_trade_delta'],'breadth',c['breadth_pass'],'ticker+',c['ticker']['positive_groups'],'year+',c['year']['positive_groups'],'family+',c['family']['positive_groups'],'CI',c['ticker_cluster_bootstrap']['mean_delta_ci95'],flush=True)
 print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

