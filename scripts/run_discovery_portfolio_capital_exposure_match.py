#!/usr/bin/env python3
import argparse,json
from pathlib import Path
import numpy as np
from run_discovery_portfolio_capital_stage1_portfolio import load,sha,build_events,simulate,metrics,SPLIT
def match(rows,target):
 dates,en,ex,up,lens,ass=build_events(rows);W=np.ones((len(rows),1));lo,hi=1e-6,.02
 for _ in range(32):
  mid=(lo+hi)/2;w,g,c=simulate(dates,en,ex,up,W,mid,False);avg=float(g[:,0].mean())
  if avg<target:lo=mid
  else:hi=mid
 base=(lo+hi)/2;w,g,c=simulate(dates,en,ex,up,W,base,False);return base,metrics(dates,w[:,0],g[:,0],c[:,0])
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--protocol',required=True);ap.add_argument('--stage2-dev',required=True);ap.add_argument('--holdout',required=True);ap.add_argument('--output',required=True);a=ap.parse_args();z,m=load(a.cache,a.manifest);devrows=[r for r in z['rows'] if r['signal_date']<SPLIT];hrows=[r for r in z['rows'] if r['signal_date']>=SPLIT];dv=json.load(open(a.stage2_dev));hv=json.load(open(a.holdout));dmap={p['name']:p for p in dv['policies']};hmap={p['name']:p for p in hv['policies']};names=[p['name'] for p in hv['policies'][1:]]
 out={'stage':'EXPOSURE_MATCHED_BASELINE_FALSIFICATION','protocol_sha256':sha(a.protocol),'holdout_accessed_for_diagnostic':True,'verification_a_accessed':False,'verification_b_accessed':False,'candidates':[]}
 for nm in names:
  td=dmap[nm]['nonlevered']['avg_gross_exposure'];th=hmap[nm]['holdout_nonlevered']['avg_gross_exposure'];bd,md=match(devrows,td);bh,mh=match(hrows,th);cd=dmap[nm]['nonlevered'];ch=hmap[nm]['holdout_nonlevered']
  q={'name':nm,'development':{'target_avg_gross':td,'matched_baseline_base_fraction':bd,'matched_baseline':md,'candidate':cd,'candidate_minus_matched_wealth':cd['terminal_wealth']-md['terminal_wealth']},'holdout':{'target_avg_gross':th,'matched_baseline_base_fraction':bh,'matched_baseline':mh,'candidate':ch,'candidate_minus_matched_wealth':ch['terminal_wealth']-mh['terminal_wealth']}};out['candidates'].append(q);print(nm,'DEV cand/matched',cd['terminal_wealth'],md['terminal_wealth'],'HOLD cand/matched',ch['terminal_wealth'],mh['terminal_wealth'],flush=True)
 Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print('VERIFICATION_A_ACCESSED=False VERIFICATION_B_ACCESSED=False')
if __name__=='__main__':main()

