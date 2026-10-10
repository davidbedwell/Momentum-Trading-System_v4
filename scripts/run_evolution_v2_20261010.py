#!/usr/bin/env python3
"""V2 bounded evolutionary research, DEV80 only. No protected banks."""
import argparse,concurrent.futures,hashlib,json,os,pathlib,random,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_gen2_200_parent_parallel_20261010 import init_worker,evaluate,HORIZONS,digest,PARENTS
from scripts.audit_evolution_domains_20261010 import schema,valid,mutate
from scripts.evolution_safety_20261010 import atomic_json,recover_jsonl,durable_append,packed_signal,overlap
BASE=ROOT/'Research/Runs/gen2-200-parent-20261010'
DEFAULT=ROOT/'Research/Runs/gen3-v2-certified-domain'
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.strip()]
def key(c):return c['genome_hash']
def qualify(r,h):
 if r.get('status')!='EVALUATED_UNCERTIFIED':return None
 p=next((p for p in r['points'] if p['horizon']==h),None)
 if not p:return None
 n=p.get('effective_n',0);ev=p.get('ev_net');lo=p.get('lcb95')
 if n is None or n<30 or not isinstance(ev,(float,int)) or not isinstance(lo,(float,int)):return None
 import math
 return (float(lo),float(ev)) if math.isfinite(ev) and math.isfinite(lo) and ev>0 and lo>0 else None
def signal(child):
 # Execute in worker initialized with the same DEV80 compiler used by evaluation.
 from scripts.run_gen2_200_parent_parallel_20261010 import WORKER
 import numpy as np
 compiler=WORKER[0]
 mask=np.logical_and.reduce([compiler.compile(f,g) for f,g in child['chromosomes']])
 return packed_signal(mask)
def evaluate_and_signal(child):
 r=evaluate(child)
 if r['status']=='EVALUATED_UNCERTIFIED':
  try:r['signal']=signal(child)
  except Exception as e:r['status']='REJECTED_SIGNAL';r['error']=repr(e)
 return r
def pool_for(side,h,genomes,results,domains,limit=20):
 options=[]
 for hash_,c in genomes.items():
  if c['side']!=side or not valid(c['chromosomes'],domains):continue
  r=results.get(hash_)
  if not r:continue
  q=qualify(r,h)
  if q and r.get('signal') and r['signal']['count']>=30:options.append((q,c,r))
 options.sort(key=lambda x:x[0],reverse=True)
 chosen=[]
 for q,c,r in options:
  if all(overlap(r['signal'],old[2]['signal'])<.85 for old in chosen):chosen.append((q,c,r))
  if len(chosen)>=limit:break
 return chosen
def reconcile(out,config):
 candidates=out/'candidates.jsonl';evaluations=out/'evaluations.jsonl';state=out/'state.json'
 cs=recover_jsonl(candidates);rs=recover_jsonl(evaluations)
 ids=[x['genome_hash'] for x in cs]
 if len(ids)!=len(set(ids)):raise RuntimeError('Duplicate candidate hashes')
 cmap={key(c):c for c in cs};rmap={}
 for r in rs:
  k=r['genome_hash']
  if k not in cmap:raise RuntimeError('Orphan evaluation')
  if k in rmap:
   if rmap[k]!=r:raise RuntimeError('Conflicting evaluation duplicates')
  rmap[k]=r
 st=json.loads(state.read_text()) if state.exists() else None
 if st and st['config']!=config:raise RuntimeError('Frozen configuration mismatch')
 if not st:st={'config':config,'generation':0,'phase':'READY','history':[],'stagnant':0,'rng_state':None}
 # Candidate journal is the authoritative generation intent. State can lag after a crash.
 generations=sorted(set(c['generation'] for c in cs))
 if generations and generations!=list(range(1,max(generations)+1)):raise RuntimeError('Noncontiguous generations')
 for g in generations:
  batch=[c for c in cs if c['generation']==g]
  if len(batch)!=config['batch']:raise RuntimeError('Partial candidate generation; fail closed')
 if st['generation']>len(generations):raise RuntimeError('State ahead of journal')
 if len(generations)>st['generation']+1:raise RuntimeError('Multiple uncommitted generations')
 if len(generations)==st['generation']+1 and not (out/'pending.json').exists():raise RuntimeError('Pending RNG checkpoint missing')
 return st,cmap,rmap
def main():
 p=argparse.ArgumentParser()
 p.add_argument('--output',type=pathlib.Path,default=DEFAULT)
 p.add_argument('--generations',type=int,default=200);p.add_argument('--batch',type=int,default=120)
 p.add_argument('--workers',type=int,default=6);p.add_argument('--seed',type=int,default=20261010)
 p.add_argument('--dry-run',action='store_true');a=p.parse_args()
 assert 1<=a.workers<=64 and 1<=a.generations<=200 and 10<=a.batch<=1000
 out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
 domains=schema()
 # Preserve legacy checkpoint schema: 'workers' records the original 6-worker run, not current execution parallelism.
 config={'seed':a.seed,'batch':a.batch,'workers':6,'domain_sha256':hashlib.sha256(json.dumps(domains,sort_keys=True).encode()).hexdigest(),'gen2_sha256':hashlib.sha256((BASE/'offspring.jsonl').read_bytes()).hexdigest()}
 st,cmap,rmap=reconcile(out,config)
 parents=rows(PARENTS);orig=rows(BASE/'offspring.jsonl');historical=parents+orig
 # Preserve all Gen2 definitions; only in-domain parents breed.
 genomes={c['genome_hash']:c for c in orig}
 for c in parents:genomes[digest((c['side'],c['chromosomes']))]=dict(c,genome_hash=digest((c['side'],c['chromosomes'])))
 genomes.update(cmap)
 results={}
 for r in rows(BASE/'evaluations.jsonl'):results[r['genome_hash']]=r
 results.update(rmap)
 # Bootstrap bounded Gen2 leaders' actual signals once, with durable cache.
 seed_path=out/'seed_signals.jsonl'
 seed_cache={r['genome_hash']:r for r in recover_jsonl(seed_path)}
 seeds=[]
 for side in ('LONG','SHORT'):
  for h in HORIZONS:
   options=[c for c in orig if c['side']==side and valid(c['chromosomes'],domains) and qualify(results.get(key(c),{}),h)]
   options.sort(key=lambda c:qualify(results[key(c)],h),reverse=True)
   for c in options[:15]:
    if key(c) not in seed_cache:seeds.append(c)
 seeds=list({key(c):c for c in seeds}.values())
 if seeds and not a.dry_run:
  with concurrent.futures.ProcessPoolExecutor(max_workers=min(a.workers,a.batch),initializer=init_worker) as executor:
   for r in executor.map(evaluate_and_signal,seeds,chunksize=1):
    durable_append(seed_path,[r]);seed_cache[r['genome_hash']]=r
 for hash_,r in seed_cache.items():
  if hash_ in results and r.get('signal'):
   results[hash_]=dict(results[hash_],signal=r['signal'])
 rng=random.Random(a.seed)
 if st['rng_state']:
  def tup(x):return tuple(tup(y) for y in x) if isinstance(x,list) else x
  rng.setstate(tup(st['rng_state']))
 # For deterministic crash recovery, pending generation stores RNG state after generation.
 for gen in range(st['generation']+1,a.generations+1):
  pending=[c for c in cmap.values() if c['generation']==gen]
  if pending:
   if not (out/'pending.json').exists():raise RuntimeError('Missing pending RNG checkpoint')
   pending_state=json.loads((out/'pending.json').read_text())
   if pending_state['generation']!=gen:raise RuntimeError('Pending generation mismatch')
   rng.setstate(tup(pending_state['rng_state']))
  else:
   from scripts.evolution_active_dedup_fast_20261010 import curate
   curated=curate(genomes,results,domains,HORIZONS)
   allowed={(x['side'],x['horizon'],x['genome_hash']) for x in curated['active']}
   niches=[]
   for side in ('LONG','SHORT'):
    for h in HORIZONS:
     pool=[x for x in pool_for(side,h,genomes,results,domains) if (side,h,key(x[1])) in allowed]
     if len(pool)>=2:niches.append((side,h,pool))
   if not niches:
    print('NO_ELIGIBLE_NICHES: need baseline signals before breeding',flush=True);break
   pending=[];known=set(genomes);niche_attempts={ (side,h):0 for side,h,_ in niches }
   for attempt in range(a.batch*300):
    if len(pending)>=a.batch:break
    side,h,pool=niches[attempt%len(niches)]
    niche_attempts[(side,h)]+=1
    x,y=rng.sample(pool,2)
    # Recombination of validated complete family blocks; at least one bounded mutation.
    genes={f:json.loads(json.dumps(g)) for f,g in x[1]['chromosomes']}
    if rng.random()<.5:
     f,g=rng.choice(y[1]['chromosomes']);genes[f]=json.loads(json.dumps(g))
    g=mutate(sorted(genes.items()),rng,domains)
    if not valid(g,domains):continue
    hash_=digest((side,g))
    if hash_ in known:continue
    known.add(hash_)
    pending.append({'generation':gen,'offspring_id':gen*100000+len(pending)+1,'genome_hash':hash_,'side':side,'chromosomes':g,'target_horizon':h,'parent_hashes':[key(x[1]),key(y[1])]})
   if len(pending)<a.batch:
    print('NOVELTY_EXHAUSTED',len(pending),flush=True);break
   if a.dry_run:
    print('PREFLIGHT',gen,'niches',len(niches),'valid_children',len(pending));return
   atomic_json(out/'pending.json',{'generation':gen,'rng_state':list(rng.getstate())})
   durable_append(out/'candidates.jsonl',pending)
   cmap.update({key(c):c for c in pending})
  todo=[c for c in pending if key(c) not in rmap]
  if todo:
   with concurrent.futures.ProcessPoolExecutor(max_workers=min(a.workers,a.batch),initializer=init_worker) as executor:
    for r in executor.map(evaluate_and_signal,todo,chunksize=1):
     durable_append(out/'evaluations.jsonl',[r]);rmap[r['genome_hash']]=r;results[r['genome_hash']]=r
  if any(key(c) not in rmap for c in pending):raise RuntimeError('Incomplete generation')
  for c in pending:genomes[key(c)]=c
  # Novelty counts distinct actual trading signals, not merely different gene strings.
  accepted=0;archive={}
  # Compare against the existing cross-generation archive, not just siblings.
  previous={}
  pending_keys={key(x) for x in pending}
  prior_genomes={k:v for k,v in genomes.items() if k not in pending_keys}
  for side in ('LONG','SHORT'):
   for h in HORIZONS:
    previous[(side,h)]=pool_for(side,h,prior_genomes,results,domains)
  for c in pending:
   h=c['target_horizon'];r=rmap[key(c)];q=qualify(r,h)
   if not q or not r.get('signal') or r['signal']['count']<30:continue
   niche=(c['side'],h);incumbents=archive.setdefault(niche,[])
   # A near-identical trade signal only counts as progress if it improves LCB.
   redundant=any(overlap(r['signal'],old[2]['signal'])>=.85 and old[0][0]>=q[0] for old in previous[niche])
   redundant=redundant or any(overlap(r['signal'],old['signal'])>=.85 for old in incumbents)
   if not redundant:incumbents.append(r);accepted+=1
  from scripts.evolution_active_dedup_fast_20261010 import curate
  curated=curate(genomes,results,domains,HORIZONS)
  atomic_json(out/'active_population.json',curated)
  st['generation']=gen;st['stagnant']=st['stagnant']+1 if accepted==0 else 0
  st['history'].append({'generation':gen,'evaluated':len(pending),'distinct_positive_target_signals':accepted})
  st['rng_state']=list(rng.getstate());st['phase']='COMPLETE'
  atomic_json(out/'state.json',st)
  (out/'pending.json').unlink(missing_ok=True)
  print('GEN',gen,'EVALUATED',len(pending),'DISTINCT_POSITIVE',accepted,flush=True)
  if st['stagnant']>=8:break
if __name__=='__main__':main()
