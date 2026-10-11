#!/usr/bin/env python3
"""Fresh, retrospective Normal-only GA4; no historical parent fitness or population reuse."""
import argparse,concurrent.futures,hashlib,json,os,pathlib,random,sys
import numpy as np
import pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_gen2_200_parent_parallel_20261010 import HORIZONS,digest,PRED,init_worker
from scripts.audit_evolution_domains_20261010 import schema,valid,mutate
from scripts.evolution_safety_20261010 import atomic_json,durable_append,recover_jsonl,packed_signal
from Core.layered_ga.ga4_oracle_crash_mask import admissible_decisions
from scripts.run_evolution_v2_20261010 import qualify,pool_for
from scripts.ga4_rolling_progress_20261011 import frontier,checkpoint
from scripts.evolution_active_dedup_fast_20261010 import curate
from scripts.parallel_evolution_selection_20261011 import parallel_niches
from scripts.evolution_safety_20261010 import overlap
EPISODES=ROOT/'Research/Protocols/MTS_REENTRY_THREE_HYPOTHESIS_TEST_FREEZE_20261004.json'
DEFAULT=ROOT/'Research/Runs/ga4-normal-restored-20261011'
ADMISSIBLE=None

def worker_init():
 global ADMISSIBLE
 init_worker()
 frame=pd.read_parquet(PRED,columns=['effective_date'])
 episodes=json.loads(EPISODES.read_text())['episodes']
 ADMISSIBLE=admissible_decisions(frame['effective_date'],frame['effective_date'],episodes,HORIZONS,offset=10)

def evaluate(c):
 from scripts.run_gen2_200_parent_parallel_20261010 import WORKER
 compiler,paths,costs,clusters,curve=WORKER
 try:
  mask=np.logical_and.reduce([compiler.compile(f,g) for f,g in c['chromosomes']])
  points=[]
  for j,h in enumerate(HORIZONS):
   # The horizon-specific eligibility is applied BEFORE fitness calculation.
   result=curve(mask & ADMISSIBLE[:,j],paths,costs,c['side'],clusters,horizons=(h,))
   points.extend(result.points)
  # Signal overlap is based on entries admissible for at least one horizon.
  sig=packed_signal(mask & ADMISSIBLE.any(axis=1))
  return {'genome_hash':c['genome_hash'],'status':'EVALUATED_UNCERTIFIED','points':points,'signal':sig}
 except Exception as exc:
  return {'genome_hash':c['genome_hash'],'status':'REJECTED','error':repr(exc)}

def fresh(rng,domains,side,known):
 families=list(domains)
 for _ in range(20000):
  selected=rng.sample(families,rng.randint(1,min(3,len(families))))
  genes=sorted((f,{k:rng.choice(s['values'] if s['kind']=='categorical' else s['original_grid']) for k,s in domains[f].items()}) for f in selected)
  if not valid(genes,domains):continue
  hash_=digest((side,genes))
  if hash_ not in known:
   known.add(hash_);return {'side':side,'chromosomes':genes,'genome_hash':hash_}
 raise RuntimeError('fresh novelty exhausted')

def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,default=DEFAULT);p.add_argument('--generations',type=int,default=200);p.add_argument('--batch',type=int,default=120);p.add_argument('--seed-size',type=int,default=1200);p.add_argument('--workers',type=int,default=6);p.add_argument('--seed',type=int,default=20261011);p.add_argument('--preflight',action='store_true');p.add_argument('--rolling-stop',action='store_true');a=p.parse_args()
 if not (1<=a.generations<=1000000 and 1<=a.workers<=64 and a.batch>=20 and a.seed_size>=a.batch):raise ValueError('invalid settings')
 domains=schema();ep=json.loads(EPISODES.read_text())['episodes'];frame=pd.read_parquet(PRED,columns=['effective_date'])
 admissible=admissible_decisions(frame.effective_date,frame.effective_date,ep,HORIZONS,offset=10)
 if not admissible.any():raise RuntimeError('No admissible Normal entries')
 config={'generations':a.generations,'batch':a.batch,'seed_size':a.seed_size,'seed':a.seed,'horizons':HORIZONS,'domain_sha256':digest(domains),'episodes_sha256':hashlib.sha256(EPISODES.read_bytes()).hexdigest(),'mask_policy':'ORACLE_PEAK_PLUS_10_TO_TROUGH_PLUS_10_FULL_PATH_EXCLUSION','population':'FRESH_RANDOM_NO_LEGACY_PARENT_FITNESS','scope':'DEV80_ONLY','sides':['LONG'],'evolution':'RESTORED_CURATED_DIVERSITY_LCB_FIRST','rolling_stop':True}
 if a.preflight:
  print('PREFLIGHT_PASS',json.dumps({'rows':len(frame),'admissible_by_horizon':dict(zip(HORIZONS,admissible.sum(axis=0).astype(int).tolist())),'families':list(domains),'config':config}),flush=True);return
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 cp=out/'state.json';state=json.loads(cp.read_text()) if cp.exists() else None
 if state and state['config']!=json.loads(json.dumps(config)):raise RuntimeError('configuration mismatch')
 rng=random.Random(a.seed)
 if state:
  def tup(x):return tuple(tup(y) for y in x) if isinstance(x,list) else x
  rng.setstate(tup(state['rng_state']))
 else:state={'config':config,'generation':-1,'rng_state':None,'history':[]}
 cs=recover_jsonl(out/'candidates.jsonl');rs=recover_jsonl(out/'evaluations.jsonl')
 genomes={c['genome_hash']:c for c in cs};results={r['genome_hash']:r for r in rs};known=set(genomes)
 # A journaled generation may be resumed after a crash without resampling offspring.
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=worker_init) as executor:
  for gen in range(state['generation']+1,a.generations+1):
   pending=[c for c in cs if c['generation']==gen]
   if not pending:
    if gen==0:
     pending=[dict(fresh(rng,domains,'LONG',known),generation=0) for i in range(a.seed_size)]
    else:
     niches=[('LONG',h,pool) for h,pool in parallel_niches(genomes,results,domains,HORIZONS,workers=9)]
     if not niches:raise RuntimeError('NO_ELIGIBLE_NICHES: cannot breed; stop for audit')
     for i in range(a.batch):
      for attempt in range(5000):
       side,h,pool=niches[(i+attempt)%len(niches)]
       x,y=rng.sample(pool,2)
       genes={f:json.loads(json.dumps(g)) for f,g in x[1]['chromosomes']}
       if rng.random()<.5:
        f,g=rng.choice(y[1]['chromosomes']);genes[f]=json.loads(json.dumps(g))
       child=mutate(sorted(genes.items()),rng,domains)
       hash_=digest((side,child))
       if valid(child,domains) and hash_ not in known:
        known.add(hash_);pending.append({'generation':gen,'side':side,'chromosomes':child,'genome_hash':hash_,'target_horizon':h,'parent_hashes':[x[1]['genome_hash'],y[1]['genome_hash']]});break
      else:raise RuntimeError('NOVELTY_EXHAUSTED')
    atomic_json(out/'pending.json',{'generation':gen,'rng_state':list(rng.getstate())})
    durable_append(out/'candidates.jsonl',pending);cs.extend(pending);genomes.update({c['genome_hash']:c for c in pending})
   else:
    pending_state=json.loads((out/'pending.json').read_text());rng.setstate(tup(pending_state['rng_state']))
   if any(c['side']!='LONG' for c in pending):raise RuntimeError('SHORT_CANDIDATE_FORBIDDEN')
   todo=[c for c in pending if c['genome_hash'] not in results]
   from scripts.ga4_durable_batching_20261011 import journal_evaluations
   journal_evaluations(executor.map(evaluate,todo,chunksize=1),out/'evaluations.jsonl',results,batch_size=8)
   if any(c['genome_hash'] not in results for c in pending):raise RuntimeError('incomplete generation')
   previous={h:pool_for('LONG',h,{k:v for k,v in genomes.items() if k not in {c['genome_hash'] for c in pending}},results,domains) for h in HORIZONS}
   distinct=0
   for c in pending:
    h=c.get('target_horizon');r=results[c['genome_hash']]
    if h is None or not qualify(r,h) or not r.get('signal') or r['signal']['count']<30:continue
    q=qualify(r,h)
    if not any(overlap(r['signal'],old[2]['signal'])>=.85 and old[0][0]>=q[0] for old in previous[h]):distinct+=1
   accepted=sum(bool(qualify(results[c['genome_hash']],h)) for c in pending for h in HORIZONS)
   state.update(generation=gen,rng_state=list(rng.getstate()))
   state['history'].append({'generation':gen,'evaluated':len(pending),'positive_horizon_pairs':accepted,'distinct_positive_target_signals':distinct})
   atomic_json(cp,state);(out/'pending.json').unlink(missing_ok=True)
   print('GEN',gen,'EVALUATED',len(pending),'POSITIVE_HORIZON_PAIRS',accepted,flush=True)
   if gen and gen%25==0:
    journal=out/'progress_checkpoints.jsonl'
    prior=recover_jsonl(journal)
    snapshot=frontier(results.values(),HORIZONS)
    verdict=checkpoint(prior,snapshot,gen)
    if verdict is None:raise RuntimeError('missing checkpoint')
    durable_append(journal,[verdict])
    print('PROGRESS_CHECKPOINT',json.dumps(verdict),flush=True)
    if verdict['stop']:
     print('ROLLING_STOP',gen,flush=True);break
if __name__=='__main__':main()
