#!/usr/bin/env python3
import argparse,json,copy
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
from run_discovery_portfolio_capital_stage2 import causal_hierarchy
CAPS=[('NONE',None,None),('ATR8','atr',8.0),('ATR10','atr',10.0),('ATR12','atr',12.0),('PCT25','pct',.25),('PCT30','pct',.30),('PCT40','pct',.40)]
def apply(score,scale,floor,cap):
 w=np.ones(len(score));m=np.isfinite(score);w[m]=np.clip(np.maximum(score[m],0)*scale,floor,cap);return w
def cap_rows(rows,typ,x):
 if typ is None:return rows,0
 out=[];hits=0
 for r in rows:
  if typ=='atr' and not r.get('atr'):out.append(r);continue
  level=float(r['ep'])-x*float(r['atr']) if typ=='atr' else float(r['ep'])*(1-x);hit=None;fill=None
  for j,z in enumerate(r['path']):
   op=float(z['open']);lo=float(z['low'])
   if op<=level:hit=j;fill=op;break
   if lo<=level:hit=j;fill=level;break
  if hit is None:out.append(r);continue
  q=dict(r);p=[dict(z) for z in r['path'][:hit+1]];p[-1]['close']=float(fill);q['path']=p;q['exitp']=float(fill);q['ret']=float(fill)/float(r['ep'])-1;out.append(q);hits+=1
 return out,hits
def tmetric(rows,w):
 a=np.asarray([r['ret'] for r in rows])*w;q=np.quantile(a,.05);return {'mean':float(a.mean()),'p05':float(q),'cvar05':float(a[a<=q].mean()),'total_return_units':float(a.sum())}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--nominees',required=True);ap.add_argument('--stage2-dev',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 z,m=load(a.cache,a.manifest);rows=[r for r in z['rows'] if r['signal_date']<SPLIT];nom=json.load(open(a.nominees));dev=json.load(open(a.stage2_dev));risks,ev,_=causal_hierarchy(rows);score=np.divide(np.maximum(ev,0),risks['p10_loss'],out=np.full(len(rows),np.nan),where=np.isfinite(ev)&np.isfinite(risks['p10_loss'])&(risks['p10_loss']>0))
 names=['equal_weight'];cols=[np.ones(len(rows))]
 for n in nom['nominees']:
  c=n['calibration'];names.append(n['policy_name']);cols.append(apply(score,c['score_scale'],c['floor'],c['cap']))
 W=np.column_stack(cols);base=float(dev['portfolio_assumptions']['base_trade_fraction']);out={'stage':'DEVELOPMENT_CATASTROPHIC_PROTECTION_SENSITIVITY','protocol_sha256':sha(a.protocol),'code_sha256':sha(__file__),'holdout_accessed_for_results':False,'verification_a_accessed':False,'verification_b_accessed':False,'layers':[]}
 for lab,typ,x in CAPS:
  rr,hits=cap_rows(rows,typ,x);dates,en,ex,up,lens,ass=build_events(rr);ww,gg,cc=simulate(dates,en,ex,up,W,base,False);pol=[]
  for j,nm in enumerate(names):pol.append({'name':nm,'trade_metrics':tmetric(rr,W[:,j]),'nonlevered':metrics(dates,ww[:,j],gg[:,j],cc[:,j])})
  out['layers'].append({'layer':lab,'type':typ,'threshold':x,'stop_hits':hits,'stop_rate':hits/len(rows),'policies':pol});print('LAYER',lab,'HITS',hits,'RATE',hits/len(rows),flush=True)
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('OUTPUT',a.output);print('HOLDOUT_ACCESSED_FOR_RESULTS=False');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

