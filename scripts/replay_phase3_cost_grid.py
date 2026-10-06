#!/usr/bin/env python3
import argparse,json,math,multiprocessing as mp
from pathlib import Path
from run_cross_sectional_ga_phase3 import load_rows,causal_evidence_levels,choose_evidence,prep,simulate,baseline_sim
CTX=None
def work(job):
 k,item=job;rows,levels,pct,dates,sig,updates,basefs=CTX;ch=item['chromosome'];features=[choose_evidence(x,ch)[0] for x in levels]
 rec={'index':k,'chromosome':ch,'fitness_10bps':item['metrics'],'costs':{}}
 for cost in [0,5,10,15,20]:
  m=simulate(ch,rows,features,pct,dates,sig,updates,cost,detail=True,baseline_path=basefs[cost]['wealth_path'])
  rec['costs'][str(cost)]={x:y for x,y in m.items() if x!='wealth_path'}
 return rec
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--cache',required=True);ap.add_argument('--catalog',required=True);ap.add_argument('--input',required=True);ap.add_argument('--output',required=True);a=ap.parse_args()
 src=json.load(open(a.input));rows,_=load_rows(a.cache,a.catalog);levels=causal_evidence_levels(rows)
 basef=[choose_evidence(x,{'evidence_policy':'HARD_FALLBACK','genome_min_n':100,'family_min_n':100,'global_min_n':100,'family_borrow_penalty_bps':0,'global_borrow_penalty_bps':0,'shrinkage_prior_strength':100})[0] for x in levels]
 pct=[math.nan]*len(rows);dates,di,sig,updates=prep(rows,basef,pct);basefs={c:baseline_sim(rows,basef,dates,sig,updates,c) for c in [0,5,10,15,20]}
 global CTX;CTX=(rows,levels,pct,dates,sig,updates,basefs);jobs=list(enumerate(src['pareto']))
 with mp.get_context('fork').Pool(5) as pool:
  out=[]
  for n,rec in enumerate(pool.imap_unordered(work,jobs),1):out.append(rec);print('DONE',n,'/',len(jobs),flush=True)
 out.sort(key=lambda z:z['index']);Path(a.output).write_text(json.dumps({'format':'MTS_PHASE3_FROZEN_PARETO_COST_GRID_V1','source':a.input,'cost_bps':[0,5,10,15,20],'chromosomes':out},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
