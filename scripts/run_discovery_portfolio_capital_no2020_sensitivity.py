#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_capital_stage2 import causal_hierarchy

def apply_score(score,scale,floor,cap):
 a=np.asarray(score,float); w=np.ones(len(a),float); m=np.isfinite(a)
 w[m]=np.clip(np.maximum(a[m],0.0)*scale,floor,cap); return w

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--cache',required=True); ap.add_argument('--manifest',required=True); ap.add_argument('--protocol',required=True); ap.add_argument('--nominees',required=True); ap.add_argument('--output',required=True); a=ap.parse_args()
 z,m=load(a.cache,a.manifest); allrows=z['rows']; nom=json.load(open(a.nominees)); n=next(x for x in nom['nominees'] if x['role']=='growth'); c=n['calibration']
 # Compute causal histories on the original Development chronology. Exclusion is evaluation-only:
 # no refit, recalibration, or altered information set for surviving non-2020 trades.
 devall=[r for r in allrows if r['signal_date']<SPLIT]
 risks,ev,src=causal_hierarchy(devall)
 keep=np.array([str(r['signal_date'])[:4] != '2020' for r in devall])
 rows=[r for r,k in zip(devall,keep) if k]
 score=np.divide(np.maximum(ev,0),risks['p10_loss'],out=np.full(len(devall),np.nan),where=np.isfinite(ev)&np.isfinite(risks['p10_loss'])&(risks['p10_loss']>0))[keep]
 w=apply_score(score,float(c['score_scale']),float(c['floor']),float(c['cap']))
 W=np.column_stack([np.ones(len(rows)),w]); dates,entries,exits,updates,lens,ass=build_events(rows)
 base=float(ass['base_trade_fraction']); wealth,gross,cash=simulate(dates,entries,exits,updates,W,base,False)
 pol=[]
 for j,name in enumerate(['equal_weight',n['policy_name']]): pol.append({'name':name,'nonlevered':metrics(dates,wealth[:,j],gross[:,j],cash[:,j]),'mean_multiplier':float(W[:,j].mean())})
 b,q=pol; bm=b['nonlevered']; qm=q['nonlevered']
 out={'stage':'DEVELOPMENT_2020_EXCLUSION_FROZEN_SENSITIVITY','purpose':'Falsification/sensitivity only; no search, retuning, or nomination','protocol_sha256':sha(a.protocol),'nominee_manifest_sha256':sha(a.nominees),'code_sha256':sha(__file__),'cache_manifest':m,'exclusion':{'calendar_year':2020,'basis':'signal_date','removed_trades':int((~keep).sum()),'retained_trades':len(rows),'original_development_trades':len(devall)},'frozen_policy':{'name':n['policy_name'],'calibration':c},'causal_history_policy':'Original Development causal histories retained; 2020 removed only from evaluated portfolio, so non-2020 policy scores are unchanged.','holdout_accessed_for_this_analysis':False,'verification_a_accessed':False,'verification_b_accessed':False,'policies':pol,'versus_baseline':{'terminal_wealth_delta':qm['terminal_wealth']-bm['terminal_wealth'],'terminal_wealth_ratio':qm['terminal_wealth']/bm['terminal_wealth'],'cagr_delta':qm['cagr_equivalent']-bm['cagr_equivalent'],'max_drawdown_delta':qm['max_drawdown']-bm['max_drawdown'],'cvar05_delta':qm['daily_cvar05']-bm['daily_cvar05'],'return_to_drawdown_delta':qm['return_to_drawdown']-bm['return_to_drawdown']}}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n'); print(json.dumps(out['exclusion'],indent=2)); print('BASE',bm); print('FROZEN',qm); print('VS',out['versus_baseline']); print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__': main()
