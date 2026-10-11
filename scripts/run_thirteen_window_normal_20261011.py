#!/usr/bin/env python3
"""Independent 13-window Normal GA; frozen GA4 crash exclusions.
No evolutionary work without certified preflight and explicit new-server token.
"""
import argparse,concurrent.futures,hashlib,json,pathlib,random,sys
import numpy as np,pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_gen2_200_parent_parallel_20261010 import digest,PRED,init_worker
from scripts.audit_evolution_domains_20261010 import schema,valid,mutate
from scripts.evolution_safety_20261010 import atomic_json,durable_append,recover_jsonl,packed_signal,overlap
from scripts.run_evolution_v2_20261010 import qualify,pool_for
from scripts.evolution_active_dedup_fast_20261010 import curate
from scripts.parallel_evolution_selection_20261011 import parallel_niches
from scripts.ga4_rolling_progress_20261011 import frontier,checkpoint
from scripts.thirteen_window_statistical_guard_20261011 import adjusted_lcb
from scripts.thirteen_window_evolution_engine_20261011 import WINDOWS,HORIZONS
from scripts.thirteen_window_crash_mask_20261011 import mask as crash_mask,EPISODES
from scripts.thirteen_window_launch_guard_20261011 import require_launch_authorization
from scripts.thirteen_window_oct09_seeds_20261011 import load as load_legacy_seeds,seed_population
ADMISSIBLE=None
ACTIVE_HORIZONS=HORIZONS

def worker_init():
 global ADMISSIBLE,ACTIVE_HORIZONS
 init_worker()
 frame=pd.read_parquet(PRED,columns=['effective_date'])
 ADMISSIBLE=crash_mask(frame.effective_date,pd.DatetimeIndex(pd.to_datetime(frame.effective_date)).normalize().unique().sort_values())
 ACTIVE_HORIZONS=tuple(range(int(__import__('os').environ['MTS_WINDOW_LOW']),int(__import__('os').environ['MTS_WINDOW_HIGH'])+1))

def evaluate(c):
 from scripts.run_gen2_200_parent_parallel_20261010 import WORKER
 compiler,paths,costs,clusters,curve=WORKER
 try:
  signal=np.logical_and.reduce([compiler.compile(f,g) for f,g in c['chromosomes']])
  points=[]
  for j,h in enumerate(HORIZONS):
   if h not in ACTIVE_HORIZONS:continue
   r=curve(signal & ADMISSIBLE[:,j],paths,costs,c['side'],clusters,horizons=(h,))
   points.extend(r.points)
  return {'genome_hash':c['genome_hash'],'status':'EVALUATED_UNCERTIFIED','points':points,'signal':packed_signal(signal & ADMISSIBLE.any(axis=1))}
 except Exception as exc:
  return {'genome_hash':c['genome_hash'],'status':'REJECTED','error':repr(exc)}

def fresh(rng,domains,side,known):
 families=list(domains)
 for _ in range(20000):
  selected=rng.sample(families,rng.randint(1,min(3,len(families))))
  genes=sorted((f,{k:rng.choice(s['values'] if s['kind']=='categorical' else s['original_grid']) for k,s in domains[f].items()}) for f in selected)
  if not valid(genes,domains):continue
  key=digest((side,genes))
  if key not in known:known.add(key);return {'side':side,'chromosomes':genes,'genome_hash':key}
 raise RuntimeError('fresh novelty exhausted')

def main():
 p=argparse.ArgumentParser()
 p.add_argument('--output',type=pathlib.Path,default=ROOT/'Research/Runs/thirteen-window-normal-20261011')
 p.add_argument('--generations',type=int,default=1000000);p.add_argument('--batch',type=int,default=120)
 p.add_argument('--seed-size',type=int,default=1200);p.add_argument('--workers',type=int,default=28)
 p.add_argument('--seed',type=int,default=20261011);p.add_argument('--authorization-file',type=pathlib.Path)
 p.add_argument('--window',type=int,nargs=2,metavar=('LOW','HIGH'),required=True)
 p.add_argument('--preflight',action='store_true');a=p.parse_args()
 if not (1<=a.generations<=1000000 and 1<=a.workers<=64 and a.batch>=20 and a.seed_size>=a.batch):raise ValueError('invalid settings')
 if tuple(a.window) not in WINDOWS:raise ValueError('invalid window')
 window=tuple(a.window);target_horizons=tuple(range(window[0],window[1]+1))
 domains=schema();legacy_seeds,legacy_sha=load_legacy_seeds(domains);initial_count=a.seed_size+len(legacy_seeds)
 frame=pd.read_parquet(PRED,columns=['effective_date'])
 allowed=crash_mask(frame.effective_date,pd.DatetimeIndex(pd.to_datetime(frame.effective_date)).normalize().unique().sort_values())
 if a.preflight:
  print(json.dumps({'status':'DATA_ONLY_PREFLIGHT_NO_LAUNCH','rows':len(frame),'window':window,'horizons':target_horizons,'eligible_per_horizon':allowed[:,[h-2 for h in target_horizons]].sum(axis=0).tolist(),'domain_count':len(domains)}));return
 # This call MUST precede output creation, workers, or any genome evaluation.
 require_launch_authorization(authorization_path=a.authorization_file)
 config={'generations':a.generations,'batch':a.batch,'seed_size':a.seed_size,'seed':a.seed,'horizons':target_horizons,'window':window,'domain_sha256':digest(domains),'episodes_sha256':hashlib.sha256(EPISODES.read_bytes()).hexdigest(),'mask_policy':'GA4_ORACLE_FULL_PATH_EXCLUSION','scope':'DEV80_ONLY','population':'RANDOM_1200_PLUS_OCT09_23_REEVALUATED','legacy_seed_sha256':legacy_sha,'legacy_seed_count':len(legacy_seeds),'initial_population_count':initial_count,'evolution':'GA4_CURATED_MULTIPLICITY_ADJUSTED_EXPLORATORY','side':'LONG'}
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 cp=out/'state.json';state=json.loads(cp.read_text()) if cp.exists() else None
 if state and state['config']!=json.loads(json.dumps(config)):raise RuntimeError('configuration mismatch')
 rng=random.Random(a.seed)
 def tup(x):return tuple(tup(y) for y in x) if isinstance(x,list) else x
 if state:rng.setstate(tup(state['rng_state']))
 else:state={'config':config,'generation':-1,'rng_state':None,'history':[]}
 if state.get('completed'):
  print('WINDOW_ALREADY_COMPLETE',window,flush=True);return
 cs=recover_jsonl(out/'candidates.jsonl');rs=recover_jsonl(out/'evaluations.jsonl')
 candidate_hashes=[c['genome_hash'] for c in cs]
 if len(candidate_hashes)!=len(set(candidate_hashes)):raise RuntimeError('DUPLICATE_CANDIDATE_HASH')
 candidate_set=set(candidate_hashes)
 if any(r['genome_hash'] not in candidate_set for r in rs):raise RuntimeError('ORPHAN_EVALUATION')
 if len({r['genome_hash'] for r in rs})!=len(rs):raise RuntimeError('DUPLICATE_EVALUATION')
 if any(c['generation']<0 for c in cs):raise RuntimeError('NEGATIVE_GENERATION')
 if cs and sorted(set(c['generation'] for c in cs))!=list(range(max(c['generation'] for c in cs)+1)):raise RuntimeError('NONCONTIGUOUS_GENERATIONS')
 for g in set(c['generation'] for c in cs):
  count=sum(c['generation']==g for c in cs)
  if count!=(initial_count if g==0 else a.batch):raise RuntimeError('PARTIAL_CANDIDATE_GENERATION')
 if cs and max(c['generation'] for c in cs)>state['generation']+1:raise RuntimeError('JOURNAL_AHEAD_OF_CHECKPOINT')
 if cs and max(c['generation'] for c in cs)==state['generation']+1 and not (out/'pending.json').is_file():raise RuntimeError('MISSING_PENDING_RNG')
 if state['generation']>=0 and (not cs or max(c['generation'] for c in cs)<state['generation']):raise RuntimeError('CHECKPOINT_AHEAD_OF_JOURNAL')
 genomes={c['genome_hash']:c for c in cs};results={r['genome_hash']:r for r in rs};known=set(genomes)
 import os
 os.environ['MTS_WINDOW_LOW']=str(window[0]);os.environ['MTS_WINDOW_HIGH']=str(window[1])
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=worker_init) as executor:
  for gen in range(state['generation']+1,a.generations+1):
   pending=[c for c in cs if c['generation']==gen]
   if not pending:
    if gen==0:
     pending,check_sha=seed_population(rng,domains,a.seed_size,fresh)
     if check_sha!=legacy_sha:raise RuntimeError('LEGACY_SEED_SOURCE_CHANGED')
     known.update(c['genome_hash'] for c in pending)
    else:
     adjusted_results=adjust_for_selection(results,target_horizons)
     niches=parallel_niches(genomes,adjusted_results,domains,target_horizons,workers=5)
     if not niches:
      # A frozen eligibility screen can legitimately extinguish the breeding pool.
      # Stop this window without weakening scientific gates or fabricating offspring.
      state['completed']=True
      state['stop_reason']='ELIGIBLE_PARENT_POOL_EXTINCT'
      state['extinction_generation']=gen
      atomic_json(cp,state)
      print('ELIGIBLE_PARENT_POOL_EXTINCT',gen,'LAST_COMPLETED',state['generation'],flush=True)
      break
     for i in range(a.batch):
      for attempt in range(5000):
       h,pool=niches[(i+attempt)%len(niches)];x,y=rng.sample(pool,2)
       genes={f:json.loads(json.dumps(g)) for f,g in x[1]['chromosomes']}
       if rng.random()<.5:
        f,g=rng.choice(y[1]['chromosomes']);genes[f]=json.loads(json.dumps(g))
       child=mutate(sorted(genes.items()),rng,domains);key=digest(('LONG',child))
       if valid(child,domains) and key not in known:
        known.add(key);pending.append({'generation':gen,'side':'LONG','chromosomes':child,'genome_hash':key,'target_horizon':h,'parent_hashes':[x[1]['genome_hash'],y[1]['genome_hash']],'seed_origin':'EVOLVED','ancestor_legacy_ids':[{'generation':g,'id':i} for g,i in sorted({(v['generation'],v['id']) for parent in (x[1],y[1]) for v in parent.get('ancestor_legacy_ids',[])})]});break
      else:
       # Frozen 5,000-attempt novelty budget exhausted: end this window without
       # weakening the mutation, validity, deduplication, or selection policy.
       state['completed']=True
       state['stop_reason']='NOVELTY_EXHAUSTED'
       state['novelty_exhaustion_generation']=gen
       state['novelty_exhaustion_offspring_index']=i
       state['novelty_exhaustion_attempt_limit']=5000
       atomic_json(cp,state)
       print('NOVELTY_EXHAUSTED',gen,'OFFSPRING_INDEX',i,'LAST_COMPLETED',state['generation'],flush=True)
       return
    atomic_json(out/'pending.json',{'generation':gen,'rng_state':list(rng.getstate())})
    durable_append(out/'candidates.jsonl',pending);cs.extend(pending);genomes.update({c['genome_hash']:c for c in pending})
   else:
    if len(pending)!=(initial_count if gen==0 else a.batch):raise RuntimeError('INCOMPLETE_CANDIDATE_GENERATION')
    pending_state=json.loads((out/'pending.json').read_text())
    if pending_state['generation']!=gen:raise RuntimeError('PENDING_GENERATION_MISMATCH')
    rng.setstate(tup(pending_state['rng_state']))
   todo=[c for c in pending if c['genome_hash'] not in results]
   for r in executor.map(evaluate,todo,chunksize=1):
    durable_append(out/'evaluations.jsonl',[r]);results[r['genome_hash']]=r
   if any(c['genome_hash'] not in results for c in pending):raise RuntimeError('incomplete generation')
   state.update(generation=gen,rng_state=list(rng.getstate()))
   state['history'].append({'generation':gen,'evaluated':len(pending)})
   atomic_json(cp,state);(out/'pending.json').unlink(missing_ok=True)
   print('GEN',gen,'EVALUATED',len(pending),flush=True)
   if gen and gen%25==0:
    journal=out/'progress_checkpoints.jsonl';previous=recover_jsonl(journal)
    verdict=checkpoint(previous,frontier(adjust_for_selection(results,target_horizons).values(),target_horizons),gen)
    durable_append(journal,[verdict]);print('PROGRESS_CHECKPOINT',json.dumps(verdict),flush=True)
    if verdict['stop']:
     state['completed']=True;state['stop_reason']='ROLLING_STOP';atomic_json(cp,state)
     print('ROLLING_STOP',gen,flush=True);break
  else:
   state['completed']=True;state['stop_reason']='GENERATION_CEILING';atomic_json(cp,state)
def adjust_for_selection(results,horizons):
 out={}
 tests=max(1,len(results)*len(horizons))
 for key,r in results.items():
  points=[]
  for p in r.get('points',[]):
   q=dict(p)
   if p.get('horizon') in horizons:
    try:q['lcb95']=adjusted_lcb(p['ev_net'],p['se_cluster'],tests)
    except (ValueError,KeyError,OverflowError):q['lcb95']=float('-inf')
   points.append(q)
  out[key]=dict(r,points=points)
 return out

if __name__=='__main__':main()
