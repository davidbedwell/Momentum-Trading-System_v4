#!/usr/bin/env python3
from pathlib import Path
import os,json,time,hashlib,random,math
import numpy as np,pandas as pd
from concurrent.futures import ProcessPoolExecutor
ROOT=Path('/home/ubuntu/mts-ga-dev117-permitted-20261006')
RUN=Path('Research/Runs/layered/stage2-opportunity-v2-20261007'); RUN.mkdir(parents=True,exist_ok=True)
CTX=Path('Research/Runs/layered/stage1-context-map-20261007/galaxy_context.parquet')
SECT=Path('Research/Runs/layered/sector_metadata_dev117_20261007.json')
SEED=20261007; COST=0.0005; H=(1,3,5,10,20,63)
FAM={
'MOMENTUM':['ret20','ret63','ret126','ret252','ret252skip20'],
'BREAKOUT':['range20','range50','range252','break20','break50','rangewidthratio'],
'TREND':['gap20','gap50','gap200','slope20','slope50','slope200','pullback20'],
'MEAN_REVERSION':['rsi14','gap20','gap50','ret5','ret10','ret20','dd252','range20','z20','streak'],
'VOLATILITY':['natr14','natr20','rv20','rv63','candle','volratio','rangewidthratio'],
'VOLUME_LIQUIDITY':['relvol20','dvolrel20','amihud20','spread','volslope20','uvbal20'],
'RELATIVE_CROSS_SECTIONAL':['rank126','rank252','rank252skip20','rschange20','sectorvs63'],
'MARKET_REGIME_STRUCTURE':['breadth200','breadthpos20','advdec','nhnl252','rvrank20']}
Q=(.1,.2,.3,.5,.7,.8,.9)
def sha(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build_ticker(t):
 d=pd.read_parquet(ROOT/f'{t}.parquet').sort_values('date').copy(); d['date']=pd.to_datetime(d.date); p=d.adj_close.astype(float); r=p.pct_change()
 for n in (5,10,20,63,126,252): d[f'ret{n}']=p.pct_change(n)
 d['ret252skip20']=p.shift(20)/p.shift(252)-1
 for n in (20,50,200): d[f'gap{n}']=p/p.rolling(n).mean()-1
 d['slope20']=p.rolling(20).mean().pct_change(5);d['slope50']=p.rolling(50).mean().pct_change(10);d['slope200']=p.rolling(200).mean().pct_change(20)
 for n in (20,50,252):
  hi=p.rolling(n).max();lo=p.rolling(n).min();d[f'range{n}']=(p-lo)/(hi-lo)
 d['break20']=p/p.shift(1).rolling(20).max()-1;d['break50']=p/p.shift(1).rolling(50).max()-1;d['pullback20']=p/p.shift(1).rolling(20).max()-1
 rw20=(d.high.rolling(20).max()-d.low.rolling(20).min())/p;rw63=(d.high.rolling(63).max()-d.low.rolling(63).min())/p;d['rangewidthratio']=rw20/rw63
 delta=p.diff();up=delta.clip(lower=0).rolling(14).mean();dn=(-delta.clip(upper=0)).rolling(14).mean();d['rsi14']=100-100/(1+up/dn)
 d['dd252']=p/p.rolling(252).max()-1;d['z20']=(p-p.rolling(20).mean())/p.rolling(20).std()
 s=np.sign(r.fillna(0)); grp=(s!=s.shift()).cumsum(); d['streak']=s*s.groupby(grp).cumcount().add(1)
 tr=pd.concat([(d.high-d.low),(d.high-p.shift()).abs(),(d.low-p.shift()).abs()],axis=1).max(axis=1);d['natr14']=tr.rolling(14).mean()/p;d['natr20']=tr.rolling(20).mean()/p
 d['rv20']=r.rolling(20).std()*np.sqrt(252);d['rv63']=r.rolling(63).std()*np.sqrt(252);d['volratio']=d.rv20/d.rv63;d['candle']=(d.high-d.low)/p
 d['relvol20']=d.volume/d.volume.shift().rolling(20).mean();dv=p*d.volume;d['dvolrel20']=dv/dv.shift().rolling(20).mean();d['amihud20']=(r.abs()/dv).rolling(20).mean();d['spread']=(d.high-d.low)/((d.high+d.low)/2)
 x=np.arange(20);d['volslope20']=d.volume.rolling(20).apply(lambda a: np.polyfit(x,a,1)[0]/max(np.mean(a),1),raw=True);d['uvbal20']=(np.sign(r)*d.volume).rolling(20).sum()/d.volume.rolling(20).sum()
 for h in H:d[f'f{h}']=p.shift(-h)/p-1
 d['ticker']=t;return d[['date','ticker']+sorted(set(sum(FAM.values(),[])) & set(d.columns))+[f'f{h}' for h in H]]

def make_panel():
 cache=RUN/'dev117_features.parquet'
 if cache.exists(): return pd.read_parquet(cache)
 ts=sorted(p.stem for p in ROOT.glob('*.parquet')); w=min(6,len(ts))
 with ProcessPoolExecutor(max_workers=w) as ex: parts=list(ex.map(build_ticker,ts))
 d=pd.concat(parts,ignore_index=True).sort_values(['date','ticker'])
 # cross-sectional causal contemporaneous descriptors
 for src,out in [('ret126','rank126'),('ret252','rank252'),('ret252skip20','rank252skip20'),('rv20','rvrank20')]:
  d[out]=d.groupby('date')[src].rank(pct=True)
 d['rschange20']=d.groupby('ticker').rank126.diff(20)
 med=d.groupby('date').ret63.transform('median');d['sectorvs63']=d.ret63-med
 d['breadth200']=d.groupby('date').gap200.transform(lambda x:(x>0).mean());d['breadthpos20']=d.groupby('date').ret20.transform(lambda x:(x>0).mean())
 d['advdec']=d.groupby('date').ret5.transform(lambda x:(x>0).mean()-(x<0).mean())
 d['nhnl252']=d.groupby('date').range252.transform(lambda x:(x>.99).mean()-(x<.01).mean())
 g=pd.read_parquet(CTX)[['date','state','strength','trajectory']].copy();g['date']=pd.to_datetime(g.date);g=g.rename(columns={'state':'galaxy_state','strength':'galaxy_strength','trajectory':'galaxy_trajectory'})
 d=d.merge(g,on='date',how='left');d.to_parquet(cache,index=False);return d

def predicate_catalog(d):
 out=[]
 for fam,features in FAM.items():
  for f in features:
   if f not in d: continue
   vals=d[f].dropna()
   for q in Q:
    thr=float(vals.quantile(q));out.append({'family':fam,'feature':f,'op':'>=','q':q,'thr':thr});out.append({'family':fam,'feature':f,'op':'<=','q':q,'thr':thr})
 # environment is conditioning evidence, not mandatory permission
 for st in ['Strong Up','Up','Flat','Down','Strong Down']: out.append({'family':'CONTEXT','feature':'galaxy_state','op':'==','value':st})
 return out

def pmask(d,p):
 if p['op']=='==':return d[p['feature']].eq(p['value']).to_numpy()
 a=d[p['feature']].to_numpy();return (a>=p['thr']) if p['op']=='>=' else (a<=p['thr'])

def score(mask,y,side,ticker,dates):
 z=y[mask];z=z[np.isfinite(z)]
 if len(z)<200:return None
 s=1 if side=='LONG' else -1; gross=s*z; net=gross-COST
 # dependence-aware approximation: ticker-year clusters, not raw rows
 ix=np.flatnonzero(mask & np.isfinite(y)); keys=np.array([f'{ticker[i]}:{dates[i].year}' for i in ix]); vv=s*y[ix]-COST
 tmp=pd.DataFrame({'k':keys,'v':vv}).groupby('k').v.mean().to_numpy(); ne=len(tmp)
 if ne<20:return None
 se=float(np.std(tmp,ddof=1)/math.sqrt(ne));ev=float(np.mean(vv));lcb=ev-1.96*se
 loss=vv[vv<0];win=vv[vv>0]
 return {'n':int(len(vv)),'effective_n':int(ne),'ev_net':ev,'lcb95':lcb,'win_rate':float((vv>0).mean()),'avg_win':float(win.mean()) if len(win) else 0,'avg_loss':float(loss.mean()) if len(loss) else 0,'median_win':float(np.median(win)) if len(win) else 0,'median_loss':float(np.median(loss)) if len(loss) else 0,'cvar5':float(np.mean(np.sort(vv)[:max(1,len(vv)//20)]))}

def calibration(d,preds):
 rng=np.random.default_rng(SEED);base=rng.normal(0,.04,12000);sel=(np.arange(12000)%10==0);lad=[]
 for e in (.0025,.005,.01,.02):
  x=base.copy();x[sel]+=e; rec=float(x[sel].mean()-base[sel].mean()); lad.append({'effect':e,'recovered':rec,'relative_error':abs(rec-e)/e})
 # benchmark real predicate evaluation throughput
 y=d.f20.to_numpy();t=d.ticker.to_numpy();dt=pd.to_datetime(d.date).dt.to_pydatetime(); start=time.time();n=0
 for p in preds[:24]:
  for side in ('LONG','SHORT'):score(pmask(d,p),y,side,t,dt);n+=1
 sec=time.time()-start;return {'ladder':lad,'benchmark_evaluations':n,'benchmark_seconds':sec,'eval_per_second':n/max(sec,1e-6)}

def evolve(d,preds,budget,seed,side):
 rng=random.Random(seed);ticker=d.ticker.to_numpy();dates=pd.to_datetime(d.date).dt.to_pydatetime(); ys={h:d[f'f{h}'].to_numpy() for h in H}; masks=[pmask(d,p) for p in preds]
 cache={}
 def ev(g):
  key=tuple(sorted(g));k=(key,side)
  if k in cache:return cache[k]
  m=np.ones(len(d),bool)
  for i in key:m &= masks[i]
  best=None
  for h,y in ys.items():
   s=score(m,y,side,ticker,dates)
   if s and (best is None or s['lcb95']>best['lcb95']):best=dict(s,horizon=h)
  if best:best['complexity']=len(key);best['fitness']=best['lcb95']-.00025*(len(key)-1)
  cache[k]=best;return best
 pop=[tuple(sorted(rng.sample(range(len(preds)),rng.choice((1,1,2))))) for _ in range(32)];done=0
 while done<budget:
  ranked=sorted([(ev(g),g) for g in set(pop) if ev(g)],key=lambda x:x[0]['fitness'],reverse=True);done=len(cache)
  if not ranked:break
  elite=[g for _,g in ranked[:6]];new=elite[:]
  while len(new)<32 and len(cache)<budget:
   a=rng.choice(ranked[:min(16,len(ranked))])[1];b=rng.choice(ranked[:min(16,len(ranked))])[1];child=set(a)
   if rng.random()<.8: child |= set(rng.sample(list(b),max(1,len(b)//2)))
   if rng.random()<.2 and child: child.discard(rng.choice(tuple(child)))
   if rng.random()<.35 and len(child)<3: child.add(rng.randrange(len(preds)))
   if not child:child.add(rng.randrange(len(preds)))
   if len(child)>3:child=set(rng.sample(list(child),3))
   g=tuple(sorted(child));ev(g);new.append(g)
  pop=new
 front=sorted([(v,k) for k,v in cache.items() if v],key=lambda x:x[0]['fitness'],reverse=True)[:100]
 return [{'side':side,'genes':[preds[i] for i in k[0]],**v,'genome_hash':sha([side,[preds[i] for i in k[0]]])} for v,k in front],len(cache)

_GD=None;_GP=None;_GB=None
def _init_worker(d,preds,budget):
 global _GD,_GP,_GB;_GD=d;_GP=preds;_GB=budget
def _run_worker(task):
 side,seed=task;return evolve(_GD,_GP,_GB,seed,side)

def main():
 t0=time.time();status={'stage':2,'version':'v2','state':'PREFLIGHT','started':time.time(),'pid':os.getpid()};(RUN/'status.json').write_text(json.dumps(status,indent=2))
 d=make_panel();preds=predicate_catalog(d);cal=calibration(d,preds)
 # calibration-selected budget: target >= ~15 minutes total on Thunder, bounded 4k-20k evals/side across 4 independent populations
 eps=max(cal['eval_per_second'],.01); budget_each=int(max(1000,min(5000,eps*60*15/8)))
 projected=8*budget_each/eps
 cal.update({'predicate_count':len(preds),'budget_per_population':budget_each,'populations_per_side':4,'projected_search_seconds':projected})
 (RUN/'calibration.json').write_text(json.dumps(cal,indent=2))
 status.update(state='RUNNING',calibration=cal);(RUN/'status.json').write_text(json.dumps(status,indent=2))
 tasks=[(side,SEED+100*j+(0 if side=='LONG' else 50)) for side in ('LONG','SHORT') for j in range(4)]
 # independent populations in parallel; deterministic fixed seeds. Standalone process uses fork only after preprocessing is complete.
 import multiprocessing as mp
 results=[];total=0
 ctx=mp.get_context("fork")
 with ctx.Pool(processes=min(6,len(tasks)),initializer=_init_worker,initargs=(d,preds,budget_each)) as pool:
  outs=pool.map(_run_worker,tasks)
 for f,n in outs:results.extend(f);total+=n
 # dedupe and promotion: credible positive net EV + economic significance >= 2x baseline expected round-trip cost reference
 uniq={x['genome_hash']:x for x in results};allr=list(uniq.values())
 promoted=[x for x in allr if x['ev_net']>0 and x['lcb95']>0 and x['ev_net']>=2*COST and x['effective_n']>=30]
 def cat(x):
  fam=sorted(set(g['family'] for g in x['genes'] if g['family']!='CONTEXT'));return 'CROSS_FAMILY' if len(fam)>1 else (fam[0] if fam else 'CONTEXT')
 for x in promoted:x['category']=cat(x)
 scientific=sorted(promoted,key=lambda x:(x['lcb95'],x['effective_n'],-x['complexity']),reverse=True)
 economic=sorted(promoted,key=lambda x:(x['ev_net'],x['cvar5']),reverse=True)
 report={'objective':'credible prospective net EV; no CAGR/MDD/portfolio/sizing','calibration':cal,'evaluations':total,'unique_frontier':len(allr),'promoted_count':len(promoted),'scientific_ranking':scientific,'economic_ranking':economic,'verification50_status':'PENDING_ORIGINAL_DISCOVERY_MEMBERSHIP_RESTORE','fresh50_accessed':False,'verification_a_accessed':False,'verification_b_accessed':False,'elapsed_seconds':time.time()-t0}
 (RUN/'opportunity_bank.json').write_text(json.dumps(report,indent=2))
 decision='PASS_DEV117_PENDING_VERIFICATION50' if promoted else 'FAIL'
 gate={'decision':decision,'gate_version':'stage2-v2','promoted':len(promoted),'scientific_parameters_changed':False,'next_action':'RESTORE_ORIGINAL_DISCOVERY_PARTITION_AND_SCORE_FROZEN_NEXT50' if promoted else 'STOP_SCIENTIFIC'}
 (RUN/'gate.json').write_text(json.dumps(gate,indent=2));status.update(state=decision,finished=time.time(),elapsed_seconds=time.time()-t0);(RUN/'status.json').write_text(json.dumps(status,indent=2));print(json.dumps(gate,indent=2),flush=True)
if __name__=='__main__':main()
