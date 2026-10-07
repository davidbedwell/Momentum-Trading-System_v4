#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, os, random, time, hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from Core.g3.production import *
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings

os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1');os.environ.setdefault('NUMEXPR_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Research/G3'; PANEL=R/'MTS_G3_PRODUCTION_DESIGN_PANEL_20261007.json'
OUT=R/'MTS_G3_PRODUCTION_DISCOVERY_RESULT_20261007.json'; STATE=R/'MTS_G3_PRODUCTION_DISCOVERY_STATE_20261007.pkl'; MASTER=20261007
_WORK=None

def load_data(tickers):
    ev=build_earnings_index(tickers);dates,AX,AY,cols=aligned_evidence_with_earnings(tickers,ev,horizon=60)
    n=len(dates);dend=int(n*.20);x0=dend;x1=int(n*.80);confirm0=min(n,x1+60)
    dev={t:(AX[:dend,i,:],AY[:dend,i,:]) for i,t in enumerate(tickers)}
    discovery={t:(AX[x0:x1,i,:],AY[x0:x1,i,:]) for i,t in enumerate(tickers)}
    confirm={t:(AX[confirm0:,i,:],AY[confirm0:,i,:]) for i,t in enumerate(tickers)}
    manifest={'common_rows':n,'date_start':str(dates[0]),'date_end':str(dates[-1]),'descriptor_dev_rows':dend,'discovery_rows':x1-x0,'embargo_rows':confirm0-x1,'confirmation_rows':n-confirm0,'discovery_end':str(dates[x1-1]),'confirmation_start':str(dates[confirm0]) if confirm0<n else None}
    return dev,discovery,confirm,cols,manifest

def init_worker(data):
    global _WORK;_WORK=data

def ev_task(g):
    e10=evaluate_genome(g,_WORK,10);e20=evaluate_genome(g,_WORK,20)
    prelim=(e10.n>=50 and e10.clusters>=25 and e10.mean>0 and e20.mean>0)
    axes=bootstrap_axes(e10,stable_seed(MASTER,genome_key(g)),2000) if prelim else (e10.mean,max(0.0,-e10.mean_mae),e10.duration)
    return genome_key(g),g,e10,e20,axes,descriptor(e10)

def pareto_rank(items):
    rank={}; remaining=list(range(len(items)));r=0
    while remaining:
        front=[i for i in remaining if not any(dominates(items[j][4],items[i][4]) for j in remaining if j!=i)]
        for i in front:rank[i]=r
        remaining=[i for i in remaining if i not in set(front)];r+=1
    return rank

def novelty(desc,i,k=10):
    if len(desc)<=1:return 0.
    d=np.linalg.norm(desc-desc[i],axis=1);d=np.sort(d[d>0]);return float(d[:min(k,len(d))].mean()) if len(d) else 0.

def next_population(items,island,gen,popn,nf):
    ranks=pareto_rank(items);D=np.stack([x[5] for x in items]);nov=[novelty(D,i) for i in range(len(items))]
    order=sorted(range(len(items)),key=lambda i:(ranks[i],-nov[i],genome_key(items[i][1])))
    elite=[items[i][1] for i in order[:max(16,popn//4)]];out=list(elite);r=random.Random(stable_seed(MASTER,island,gen,'breed'))
    while len(out)<popn:
        q=r.random()
        if q<.55: child=mutate(r.choice(elite),stable_seed(MASTER,island,gen,len(out),'m'),nf)
        elif q<.85: child=mutate(crossover(r.choice(elite),r.choice(elite),stable_seed(MASTER,island,gen,len(out),'x')),stable_seed(MASTER,island,gen,len(out),'xm'),nf)
        else: child=random_genome(stable_seed(MASTER,island,gen,len(out),'fresh'),nf)
        out.append(child)
    return out[:popn],min(x[4][0] for x in [items[i] for i in order[:max(1,popn//10)]])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--islands',type=int,default=8);ap.add_argument('--population',type=int,default=256);ap.add_argument('--generations',type=int,default=200);ap.add_argument('--workers',type=int,default=60);ap.add_argument('--benchmark-only',action='store_true');a=ap.parse_args()
    if (a.islands,a.population)!=(8,256) and not a.benchmark_only:raise RuntimeError('production architecture frozen at 8x256')
    panel=json.loads(PANEL.read_text());tickers=panel['tickers'];dev_data,data,confirm_data,cols,partition_manifest=load_data(tickers);nf=len(cols);(R/'MTS_G3_PRODUCTION_PARTITION_MANIFEST_20261007.json').write_text(json.dumps(partition_manifest,indent=2)+'\n')
    pops=[[random_genome(stable_seed(MASTER,i,j,'init'),nf) for j in range(a.population)] for i in range(a.islands)]
    archive={};museum={};history=[];plateau=[0]*a.islands;active=[True]*a.islands;best=[-1e99]*a.islands;t0=time.time()
    with ProcessPoolExecutor(max_workers=a.workers,initializer=init_worker,initargs=(data,)) as ex:
      maxg=1 if a.benchmark_only else a.generations
      for gen in range(maxg):
        active_ids=[i for i in range(a.islands) if active[i]]
        tasks=[g for i in active_ids for g in pops[i]]
        results=list(ex.map(ev_task,tasks,chunksize=1))
        off=0
        for isl in active_ids:
          items=results[off:off+a.population];off+=a.population
          ranks=pareto_rank(items);D=np.stack([x[5] for x in items]);nov=[novelty(D,i) for i in range(len(items))]
          for i,x in enumerate(items):
            key=x[0];e10,e20,axes=x[2],x[3],x[4]
            if promotion(e10,e20,axes,1.0,False):archive[key]={'genome':asdict(x[1]),'axes':axes,'n':e10.n,'clusters':e10.clusters,'mean20':e20.mean,'descriptor':x[5].tolist(),'island':isl,'generation':gen}
            elif len(museum)<1024 or nov[i]>min((v['novelty'] for v in museum.values()),default=-1):museum[key]={'genome':asdict(x[1]),'novelty':nov[i],'island':isl,'generation':gen}
          pops[isl],q=next_population(items,isl,gen,a.population,nf)
          if q<=best[isl]+1e-12:plateau[isl]+=1
          else:best[isl]=q;plateau[isl]=0
          if plateau[isl]>=2:active[isl]=False
        history.append({'generation':gen,'active_islands':sum(active),'promoted':len(archive),'museum':len(museum),'elapsed':time.time()-t0})
        state={'generation':gen,'populations':pops,'active':active,'plateau':plateau,'best':best,'history':history,'archive':archive,'museum':museum}
        save_checkpoint(STATE,state);print(json.dumps(history[-1]),flush=True)
        if not any(active):break
    out={'format':'MTS_G3_PRODUCTION_DISCOVERY_V1','complete':True,'benchmark_only':a.benchmark_only,'config':vars(a),'ticker_count':len(tickers),'feature_count':nf,'seconds':time.time()-t0,'history':history,'promoted_count':len(archive),'museum_count':len(museum),'promoted':archive,'decision':'STOP_G3_DISCOVERY_NO_CANDIDATES' if not archive else 'G3_CANDIDATES_READY_FOR_SCOPE_FREEZE'}
    target=R/('MTS_G3_PRODUCTION_BENCHMARK_20261007.json' if a.benchmark_only else OUT.name);target.write_text(json.dumps(out,indent=2)+'\n');print('RESULT',target,'DECISION',out['decision'])
if __name__=='__main__':main()
