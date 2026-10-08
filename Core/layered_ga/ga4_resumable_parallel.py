"""Deterministic GA4 batch evaluator with atomic, generation-level recovery.

Workers evaluate pure candidate functions; only the coordinator writes checkpoints.
No implicit search budget: callers must supply a frozen explicit budget.
"""
from __future__ import annotations
import hashlib,json,os,pickle,random,time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from .ga4_combination_genetics import propose,combine,mutate,chromosome_key
from .stage2_nsga2_engine_v3 import Individual,environmental_selection

def key_for(ch):
 return json.dumps([list(x) for x in sorted(ch,key=chromosome_key)],sort_keys=True,separators=(',',':'))
def atomic_pickle(path,obj):
 temp=path.with_suffix('.tmp')
 with temp.open('wb') as f:pickle.dump(obj,f,protocol=5);f.flush();os.fsync(f.fileno())
 os.replace(temp,path)
def run(spaces,evaluate,*,seed,population_size,generations,workers,checkpoint_dir,identity,persist=None,max_runtime_seconds=None):
 if population_size<2 or generations<1 or workers<1:raise ValueError('Invalid explicit budget')
 if not identity:raise ValueError('Frozen run identity required')
 if max_runtime_seconds is not None and max_runtime_seconds<=0:raise ValueError('Invalid runtime ceiling')
 directory=Path(checkpoint_dir);directory.mkdir(parents=True,exist_ok=True)
 config={'seed':seed,'population_size':population_size,'generations':generations,'workers':workers,'identity':identity,'max_runtime_seconds':max_runtime_seconds,'genetics_revision':'stage2-broad-discovery-v3-strict-uniqueness'}
 config_hash=hashlib.sha256(json.dumps(config,sort_keys=True).encode()).hexdigest()
 cp=directory/'generation_state.pkl'
 if cp.exists():
  state=pickle.loads(cp.read_bytes())
  if state['config_hash']!=config_hash:raise ValueError('Checkpoint/configuration mismatch')
  rng=random.Random();rng.setstate(state['rng_state'])
  next_generation=state['next_generation'];population=state['population'];cache=state['cache'];ledger=state['ledger'];counter=state['counter'];start_wall=state['start_wall'];elapsed_prior=state.get('elapsed_active_seconds',0.0);active_started=time.monotonic()
 else:
  rng=random.Random(seed);next_generation=0;population=[];cache={};ledger=[];counter=0;start_wall=time.time();elapsed_prior=0.0;active_started=time.monotonic()
 def new(ch,parents,generation):
  nonlocal counter
  counter+=1
  return {'id':f'c{counter:07d}','chromosomes':tuple(sorted(ch,key=chromosome_key)),'parents':parents,'born':generation}
 if not population:
  initial_keys=set()
  for _ in range(population_size):
   for attempt in range(1024):
    candidate=propose(spaces,rng)
    key=key_for(candidate)
    if key not in initial_keys:break
   else:raise RuntimeError('Novelty exhausted during initialization; no duplicate admitted')
   initial_keys.add(key)
   population.append(new(candidate,[],0))
 with ProcessPoolExecutor(max_workers=workers) as executor:
  for generation in range(next_generation,generations):
   remaining=float('inf') if max_runtime_seconds is None else max_runtime_seconds-(elapsed_prior+time.monotonic()-active_started)
   prior=[x['elapsed_seconds'] for x in ledger if 'elapsed_seconds' in x]
   reserve=max(prior[-3:])*1.5 if prior else 0
   if remaining<=max(60.0,reserve):break
   generation_started=time.monotonic()
   missing={key_for(p['chromosomes']):p['chromosomes'] for p in population if key_for(p['chromosomes']) not in cache}
   keys=list(missing)
   results=list(executor.map(evaluate,(missing[k] for k in keys)))
   if persist is not None:
    for key,result in zip(keys,results):
     curve,record=result
     persist(record)
     cache[key]=curve
   else:
    cache.update(zip(keys,results))
   individuals=[Individual({'chromosomes':p['chromosomes']},cache[key_for(p['chromosomes'])],p['id']) for p in population]
   selected,ranking=environmental_selection(individuals,population_size)
   by_id={p['id']:p for p in population}
   survivors=[by_id[x.candidate_id] for x in selected]
   ledger.append({'elapsed_seconds':time.monotonic()-generation_started,'generation':generation,'evaluated':len(population),'new_evaluations':len(missing),'unique_evaluations':len(cache),'selected':[x['id'] for x in survivors],'lineage':[{'child':p['id'],'parents':p['parents']} for p in population if p['born']==generation]})
   children=[]
   if generation<generations-1:
    for _ in range(population_size):
     a,b=rng.sample(survivors,2)
     candidate=combine(a['chromosomes'],b['chromosomes'],rng)
     candidate=mutate(candidate,spaces,rng)
     existing={key_for(p['chromosomes']) for p in population+children}
     for attempt in range(32):
      if key_for(candidate) not in existing and key_for(candidate) not in cache:break
      candidate=mutate(candidate,spaces,rng) if attempt%3 else propose(spaces,rng)
     else:
      raise RuntimeError('Novelty exhausted during offspring creation; no duplicate admitted')
     children.append(new(candidate,[a['id'],b['id']],generation+1))
   population=survivors+children
   atomic_pickle(cp,{'config_hash':config_hash,'next_generation':generation+1,'population':population,'cache':cache,'ledger':ledger,'counter':counter,'rng_state':rng.getstate(),'start_wall':start_wall,'elapsed_active_seconds':elapsed_prior+time.monotonic()-active_started})
 return {'generations':ledger,'unique_evaluations':len(cache),'individuals':counter,'checkpoint':str(cp),'certified':False,'stopped_for_time':max_runtime_seconds is not None and len(ledger)<generations}
