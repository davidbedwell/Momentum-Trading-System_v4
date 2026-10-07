#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,os,random,time,hashlib,resource,signal,pickle
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
import numpy as np
from Core.g3.production import *
from Core.g3.earnings_evidence import build_earnings_index,aligned_evidence_with_earnings
os.environ.setdefault('OPENBLAS_NUM_THREADS','1');os.environ.setdefault('OMP_NUM_THREADS','1');os.environ.setdefault('MKL_NUM_THREADS','1')
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'Research/G3';PANEL=R/'MTS_G3_PRODUCTION_DESIGN_PANEL_20261007.json';MASTER=20261007;_WORK=None

def load_data(tickers):
 ev=build_earnings_index(tickers);dates,AX,AY,cols=aligned_evidence_with_earnings(tickers,ev,horizon=60);n=len(dates);dend=int(n*.20);x1=int(n*.80);c0=min(n,x1+60)
 mk=lambda a,b:{t:(AX[a:b,i,:],AY[a:b,i,:]) for i,t in enumerate(tickers)}
 return mk(0,dend),mk(dend,x1),mk(c0,n),cols,{'common_rows':n,'descriptor_dev_rows':dend,'discovery_rows':x1-dend,'embargo_rows':c0-x1,'confirmation_rows':n-c0,'date_start':str(dates[0]),'date_end':str(dates[-1]),'discovery_end':str(dates[x1-1]),'confirmation_start':str(dates[c0]) if c0<n else None}

def null_data(data,seed):
 # Frozen within-stock 60-session stationary block bootstrap of outcome rows; X is unchanged.
 out={};rng=np.random.default_rng(seed);block=60
 for t,(X,Y) in data.items():
  n=len(Y);idx=[]
  while len(idx)<n:
   s=int(rng.integers(0,n));idx.extend((np.arange(s,s+block)%n).tolist())
  out[t]=(X,Y[np.asarray(idx[:n])])
 return out

def init_worker(data):
 global _WORK;_WORK=data

def ev_task(g):
 def _to(sig,frame): raise TimeoutError('organism evaluation exceeded 120s')
 signal.signal(signal.SIGALRM,_to);signal.alarm(120)
 try:
  e10=evaluate_genome(g,_WORK,10);e15=evaluate_genome(g,_WORK,15);e20=evaluate_genome(g,_WORK,20);pre=(e10.n>=50 and e10.clusters>=25 and e15.mean>0 and e20.mean>0)
  axes=bootstrap_axes(e10,stable_seed(MASTER,genome_key(g)),2000) if pre else (e10.mean,max(0.,-e10.mean_mae),e10.duration)
  axes15=bootstrap_axes(e15,stable_seed(MASTER,genome_key(g),'15'),2000) if pre else (e15.mean,0.,e15.duration)
  return genome_key(g),g,e10,e15,e20,axes,axes15,descriptor(e10)
 except TimeoutError:
  bad=Evidence([],-1e9,-1e9,1e9,1e9,0,0);return genome_key(g),g,bad,bad,bad,(-1e9,1e9,1e9),(-1e9,1e9,1e9),np.zeros(12)
 finally: signal.alarm(0)

def pareto_rank(items):
 rank={};rem=list(range(len(items)));r=0
 while rem:
  front=[i for i in rem if not any(dominates(items[j][5],items[i][5]) for j in rem if j!=i)]
  for i in front:rank[i]=r
  S=set(front);rem=[i for i in rem if i not in S];r+=1
 return rank

def novelty(D,i,k=10):
 d=np.linalg.norm(D-D[i],axis=1);d=np.sort(d[d>0]);return float(d[:min(k,len(d))].mean()) if len(d) else 0.

def next_population(items,island,gen,popn,nf):
 ranks=pareto_rank(items);D=np.stack([x[7] for x in items]);nov=[novelty(D,i) for i in range(len(items))];rank1=sum(ranks[i]==0 for i in range(len(items)))/max(1,len(items));width=[abs(items[i][2].mean-items[i][5][0]) for i in range(len(items))];order=sorted(range(len(items)),key=(lambda i:(ranks[i],width[i],-nov[i],items[i][0])) if gen==10 and rank1>.90 else (lambda i:(ranks[i],-nov[i],width[i],items[i][0])));elite=[items[i][1] for i in order[:max(16,popn//4)]];out=list(elite);r=random.Random(stable_seed(MASTER,island,gen,'breed'))
 while len(out)<popn:
  q=r.random()
  if q<.55:c=mutate(r.choice(elite),stable_seed(MASTER,island,gen,len(out),'m'),nf)
  elif q<.85:c=mutate(crossover(r.choice(elite),r.choice(elite),stable_seed(MASTER,island,gen,len(out),'x')),stable_seed(MASTER,island,gen,len(out),'xm'),nf)
  else:c=random_genome(stable_seed(MASTER,island,gen,len(out),'fresh'),nf)
  out.append(c)
 return out[:popn]

def hv_proxy(items,norm):
 front=[x[5] for i,x in enumerate(items) if not any(dominates(y[5],x[5]) for j,y in enumerate(items) if i!=j)]
 lo,hi=norm;span=np.maximum(hi-lo,1e-12);return float(sum(max(0,(a[0]-lo[0])/span[0])*max(0,(hi[1]-a[1])/span[1])*max(0,(hi[2]-a[2])/span[2]) for a in front))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--arm',choices=['REAL','NULL'],default='REAL');ap.add_argument('--islands',type=int,default=8);ap.add_argument('--population',type=int,default=256);ap.add_argument('--generations',type=int,default=200);ap.add_argument('--workers',type=int,default=60);ap.add_argument('--benchmark-only',action='store_true');a=ap.parse_args()
 if (a.islands,a.population)!=(8,256) and not a.benchmark_only:raise RuntimeError('production architecture frozen at 8x256')
 tickers=json.loads(PANEL.read_text())['tickers'];dev,data,confirm,cols,manifest=load_data(tickers);nf=len(cols)
 if a.benchmark_only:data=dev
 R.joinpath('MTS_G3_PRODUCTION_PARTITION_MANIFEST_20261007.json').write_text(json.dumps(manifest,indent=2)+'\n')
 if a.arm=='NULL':data=null_data(data,stable_seed(MASTER,'NULL'));confirm=null_data(confirm,stable_seed(MASTER,'NULL_CONFIRM'))
 # QD calibration is descriptor-development-only and frozen before discovery outcomes are read.
 qd_gen=[random_genome(stable_seed(MASTER,'qd',j),nf) for j in range(300)]
 qd_ev=[evaluate_genome(g,dev,10) for g in qd_gen];qd_desc=np.stack([descriptor(e) for e in qd_ev]);qd=qd_fit(qd_desc);dev_axes=np.asarray([[e.mean,max(0.,-e.mean_mae),e.duration] for e in qd_ev]);hv_norm=(np.min(dev_axes,0),np.max(dev_axes,0));np.savez_compressed(R/f'MTS_G3_QD_FREEZE_{a.arm}_20261007.npz',median=qd['median'],iqr=qd['iqr'],projection=qd['projection'],centroids=qd['centroids'])
 statep=R/f'MTS_G3_{a.arm}_STATE_20261007.pkl';startgen=1
 pops=[[random_genome(stable_seed(MASTER,a.arm,i,j,'init'),nf) for j in range(a.population)] for i in range(a.islands)];active=[True]*a.islands;plateau=[0]*a.islands;hv_start=[0.]*a.islands;cells={};museum={};history=[];duplicate_merges=[]
 if not a.benchmark_only and statep.exists():
  side=statep.with_suffix('.sha256');expected=side.read_text().split()[0] if side.exists() else '';actual=hashlib.sha256(statep.read_bytes()).hexdigest()
  if expected!=actual:raise RuntimeError('CHECKPOINT_HASH_MISMATCH')
  st=load_checkpoint(statep);pops=st['populations'];active=st['active'];plateau=st['plateau'];hv_start=st['hv_start'];history=st['history'];cells=st['cells'];museum=st['museum'];duplicate_merges=st.get('duplicate_merges',[]);startgen=int(st['generation'])+1
 t0=time.time();ru0=resource.getrusage(resource.RUSAGE_CHILDREN);cpu0=ru0.ru_utime+ru0.ru_stime
 with ProcessPoolExecutor(max_workers=a.workers,initializer=init_worker,initargs=(data,)) as ex:
  for gen in range(startgen,(1 if a.benchmark_only else a.generations)+1):
   ids=[i for i in range(a.islands) if active[i]];tasks=[g for i in ids for g in pops[i]];results=list(ex.map(ev_task,tasks,chunksize=1));off=0
   mig_candidates={}
   for isl in ids:
    items=results[off:off+a.population];off+=a.population;newcells=0;D=np.stack([x[7] for x in items]);nov=[novelty(D,i) for i in range(len(items))]
    for i,x in enumerate(items):
     key,g,e10,e15,e20,axes,axes15,desc=x;temporal=temporal_thirds_positive(g,data,10) if e10.n>=50 and e10.clusters>=25 else False
     pf=perturb_positive_fraction(g,data) if contender(e10,e15,e20,temporal,1.0) else 0.
     if contender(e10,e15,e20,temporal,pf) and axes15[0]>0 and (a.arm=='NULL' or axes[0]>0):
      c=qd_cell(desc,qd);rec={'genome':asdict(g),'axes':axes,'n':e10.n,'clusters':e10.clusters,'mean15':e15.mean,'lcb15':axes15[0],'mean20':e20.mean,'temporal_thirds':temporal,'perturb_fraction':pf,'descriptor':desc.tolist(),'fired_signature':[[e.ticker,e.t] for e in e10.events],'uncertainty_width':abs(e10.mean-axes[0]),'island':isl,'generation':gen,'label':'DESIGN_PANEL_SURVIVORSHIP_EXPOSED'}
      before=len(cells.get(c,[]));merged,other=qd_duplicate_merge(cells,key,rec,qd);duplicate_merges.append({'generation':gen,'key':key,'other':other}) if merged else None;qd_insert(cells,c,key,rec) if not merged else None;newcells+=int(not merged and before==0 and len(cells.get(c,[]))>0)
     elif len(museum)<1024: museum[key]={'genome':asdict(g),'novelty':nov[i],'island':isl,'generation':gen}
    hv=hv_proxy(items,hv_norm)
    if gen%40==0:
     plateau[isl],freeze=plateau_update(gen,hv_start[isl],hv,newcells,plateau[isl]);hv_start[isl]=hv
     if freeze:active[isl]=False
    elif gen==1:hv_start[isl]=hv
    mig_candidates[isl]=items[int(np.argmax(nov))][1]
    pops[isl]=next_population(items,isl,gen,a.population,nf)
   if gen%20==0 and len(ids)>1:
    for pos,recv in enumerate(ids):
     donor=ids[pos-1]
     pops[recv][-1]=mig_candidates[donor]
   history.append({'generation':gen,'rank1_fraction_last_island':sum(v==0 for v in pareto_rank(items).values())/len(items),'active_islands':sum(active),'qd_cells':len(cells),'museum':len(museum),'elapsed':time.time()-t0});print(json.dumps(history[-1]),flush=True)
   if not a.benchmark_only:
    state={'generation':gen,'populations':pops,'active':active,'plateau':plateau,'hv_start':hv_start,'history':history,'cells':cells,'museum':museum,'duplicate_merges':duplicate_merges};statep=R/f'MTS_G3_{a.arm}_STATE_20261007.pkl';h=save_checkpoint(statep,state);statep.with_suffix('.sha256').write_text(h+'  '+statep.name+'\n');gp=R/f'MTS_G3_{a.arm}_CHECKPOINT_G{gen:03d}_20261007.pkl';gh=save_checkpoint(gp,state);gp.with_suffix('.sha256').write_text(gh+'  '+gp.name+'\n');old=sorted(R.glob(f'MTS_G3_{a.arm}_CHECKPOINT_G*_20261007.pkl'));keep=set(old[-3:]+[x for x in old if int(x.name.split('_G')[2].split('_')[0])%10==0]);[(x.unlink(),x.with_suffix('.sha256').unlink(missing_ok=True)) for x in old if x not in keep]
   if not any(active):break
 # Freeze candidate structures before untouched confirmation.
 null_discovery_max=max((rec['axes'][0] for bucket in cells.values() for _,rec in bucket),default=float('-inf'))
 # Failed confirmation is demoted; never repaired.
 promoted={};failed={}
 for c,bucket in cells.items():
  for key,rec in bucket:
   g=genome_from_dict(rec['genome']);ce=evaluate_genome(g,confirm,10);caxes=bootstrap_axes(ce,stable_seed(MASTER,a.arm,key,'confirm'),2000)
   rec['confirmation_n']=ce.n;rec['confirmation_clusters']=ce.clusters;rec['confirmation_reward_lcb']=caxes[0]
   (promoted if ce.n>=50 and ce.clusters>=25 and caxes[0]>0 else failed)[key]=rec
 ru1=resource.getrusage(resource.RUSAGE_CHILDREN);cpu1=ru1.ru_utime+ru1.ru_stime;wall=time.time()-t0;cpu_util=(cpu1-cpu0)/(max(wall,1e-9)*a.workers)
 checkpoint_projection=len(pickle.dumps({'populations':pops,'cells':cells,'museum':museum},protocol=5))*23*2
 out={'format':'MTS_G3_PRODUCTION_DISCOVERY_V2','complete':True,'arm':a.arm,'benchmark_only':a.benchmark_only,'config':vars(a),'seconds':wall,'aggregate_cpu_utilization':cpu_util,'projected_checkpoint_storage_bytes':checkpoint_projection,'history':history,'duplicate_merges':duplicate_merges,'promoted_count':len(promoted),'confirmation_failed_count':len(failed),'promoted':promoted,'confirmation_failed':failed,'null_max_stat':null_discovery_max if a.arm=='NULL' else None,'decision':'STOP_G3_DISCOVERY_NO_CANDIDATES' if not promoted else 'G3_CANDIDATES_READY_FOR_NULL_CALIBRATION'}
 target=R/(f'MTS_G3_PRODUCTION_BENCHMARK_{a.arm}_20261007.json' if a.benchmark_only else f'MTS_G3_PRODUCTION_DISCOVERY_{a.arm}_20261007.json');target.write_text(json.dumps(out,indent=2)+'\n');print('RESULT',target,'DECISION',out['decision'])
if __name__=='__main__':main()
