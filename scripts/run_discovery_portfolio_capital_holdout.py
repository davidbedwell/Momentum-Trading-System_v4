#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from collections import Counter
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_capital_stage2 import causal_hierarchy
def apply_score(score,scale,floor,cap):
 a=np.asarray(score,float);w=np.ones(len(a),float);mask=np.isfinite(a);w[mask]=np.clip(np.maximum(a[mask],0.0)*scale,floor,cap);return w
def trade_metrics(rows,w):
 a=np.asarray([r['ret'] for r in rows],float)*w;q=float(np.quantile(a,.05));eq=np.cumsum(a);pk=np.maximum.accumulate(np.r_[0,eq])[1:]
 return {'mean':float(a.mean()),'p05':q,'cvar05':float(a[a<=q].mean()),'total_return_units':float(a.sum()),'max_drawdown_return_units':float((eq-pk).min())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--nominees',required=True);ap.add_argument('--stage2-dev',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 z,m=load(a.cache,a.manifest);rows=z['rows'];nom=json.load(open(a.nominees));dev=json.load(open(a.stage2_dev));risks,ev,_=causal_hierarchy(rows);score=np.divide(np.maximum(ev,0),risks['p10_loss'],out=np.full(len(rows),np.nan),where=np.isfinite(ev)&np.isfinite(risks['p10_loss'])&(risks['p10_loss']>0))
 hi=np.array([r['signal_date']>=SPLIT for r in rows]);hold=[r for r,q in zip(rows,hi) if q];scoreh=score[hi];names=['equal_weight'];cols=[np.ones(len(hold))];cal=[{'mode':'equal_weight'}];rbscale=[1.0]
 devpol={x['name']:x for x in dev['policies']}
 for n in nom['nominees']:
  c=n['calibration'];w=apply_score(scoreh,float(c['score_scale']),float(c['floor']),float(c['cap']));names.append(n['policy_name']);cols.append(w);cal.append(c);rbscale.append(float(devpol[n['policy_name']]['risk_budget_duration_scale']))
 W=np.column_stack(cols);dates,entries,exits,updates,lens,holdass=build_events(hold);base=float(dev['portfolio_assumptions']['base_trade_fraction'])
 wa,ga,ca=simulate(dates,entries,exits,updates,W,base,False);Wr=W*np.asarray(rbscale)[None,:];wb,gb,cb=simulate(dates,entries,exits,updates,Wr,base,True)
 out={'stage':'DISCOVERY_HOLDOUT_UNCHANGED_REPLAY','protocol_sha256':sha(a.protocol),'nominee_manifest_sha256':sha(a.nominees),'code_sha256':sha(__file__),'cache_manifest':m,'split':SPLIT,'development_base_trade_fraction_frozen':base,'holdout_population':len(hold),'holdout_calendar':{'first':dates[0],'last':dates[-1],'days':len(dates)},'holdout_accessed_for_results':True,'verification_a_accessed':False,'verification_b_accessed':False,'policies':[]}
 for j,nm in enumerate(names):
  dmet=nom['baseline_nonlevered'] if j==0 else next(x['development_nonlevered'] for x in nom['nominees'] if x['policy_name']==nm);hm=metrics(dates,wa[:,j],ga[:,j],ca[:,j])
  out['policies'].append({'name':nm,'calibration':cal[j],'development_nonlevered':dmet,'holdout_nonlevered':hm,'development_to_holdout':{'terminal_wealth_ratio':float(hm['terminal_wealth']/dmet['terminal_wealth']),'cagr_delta':float(hm['cagr_equivalent']-dmet['cagr_equivalent']),'max_drawdown_delta':float(hm['max_drawdown']-dmet['max_drawdown']),'cvar05_delta':float(hm['daily_cvar05']-dmet['daily_cvar05'])},'holdout_trade_metrics':trade_metrics(hold,W[:,j]),'holdout_multiplier':{'mean':float(W[:,j].mean()),'min':float(W[:,j].min()),'max':float(W[:,j].max()),'neutral_missing':int(np.sum(~np.isfinite(scoreh)))},'holdout_risk_budget':metrics(dates,wb[:,j],gb[:,j],cb[:,j])})
 b=out['policies'][0]['holdout_nonlevered']
 for p in out['policies'][1:]:
  h=p['holdout_nonlevered'];p['versus_holdout_baseline']={'terminal_wealth_delta':float(h['terminal_wealth']-b['terminal_wealth']),'terminal_wealth_ratio':float(h['terminal_wealth']/b['terminal_wealth']),'cagr_delta':float(h['cagr_equivalent']-b['cagr_equivalent']),'max_drawdown_delta':float(h['max_drawdown']-b['max_drawdown']),'cvar05_delta':float(h['daily_cvar05']-b['daily_cvar05']),'return_to_drawdown_delta':float(h['return_to_drawdown']-b['return_to_drawdown'])}
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print('HOLDOUT_BASE',b,flush=True)
 for p in out['policies'][1:]:print('HOLDOUT_NOMINEE',p['name'],p['holdout_nonlevered'],'VS_BASE',p['versus_holdout_baseline'],flush=True)
 print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False',flush=True)
if __name__=='__main__':main()

