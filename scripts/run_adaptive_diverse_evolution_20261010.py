#!/usr/bin/env python3
"""Adaptive multi-niche evolutionary discovery. DEV80 exploratory only.
Preserves Gen2 archive; never treats exploratory scores as certification.
"""
import argparse,collections,concurrent.futures,hashlib,json,math,pathlib,random,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.run_gen2_200_parent_parallel_20261010 import init_worker,evaluate,HORIZONS,offspring,digest,PARENTS
BASE=ROOT/'Research/Runs/gen2-200-parent-20261010'
OUT=ROOT/'Research/Runs/gen3-adaptive-evolution'
def load(path):return [json.loads(x) for x in path.open()]
def append(path,rows):
 with path.open('a') as f:
  for x in rows:f.write(json.dumps(x,allow_nan=True)+'\n')
def finite(x):return isinstance(x,(int,float)) and math.isfinite(x)
def score(record):
 out={}
 for p in record['points']:
  h=p['horizon'];n=p.get('effective_n',0);ev=p.get('ev_net');lcb=p.get('lcb95')
  if n>=30 and finite(ev) and finite(lcb) and ev>0 and lcb>0:
   out[h]={'ev':ev,'lcb':lcb,'n':n,'cvar5':p.get('cvar5')}
 return out
def signature(c):
 return (c['side'],tuple(sorted((fam,json.dumps(g,sort_keys=True)) for fam,g in c['chromosomes'])))
def family_distance(a,b):
 sa={x[0] for x in a['chromosomes']};sb={x[0] for x in b['chromosomes']}
 return 1-len(sa&sb)/max(1,len(sa|sb))
def mutate(a,b,rng):
 child={fam:json.loads(json.dumps(g)) for fam,g in a['chromosomes']}
 donor={fam:g for fam,g in b['chromosomes']}
 # Mix whole validated gene blocks; side-specific populations never cross.
 for fam,g in donor.items():
  if rng.random()<.35:child[fam]=json.loads(json.dumps(g))
 if len(child)>1 and rng.random()<.2:child.pop(rng.choice(list(child)))
 if rng.random()<.15 and donor:
  fam=rng.choice(list(donor));child[fam]=json.loads(json.dumps(donor[fam]))
 # Mutate only numeric domains whose validity can be checked by the compiler.
 for fam,g in child.items():
  if rng.random()<.4:
   keys=[k for k,v in g.items() if isinstance(v,float) and not isinstance(v,bool) and 0<=v<=1]
   if keys:
    k=rng.choice(keys);g[k]=round(min(1,max(0,g[k]+rng.choice((-1,1))*rng.choice((.01,.025,.05)))),6)
 return sorted(child.items())
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--generations',type=int,default=200);ap.add_argument('--batch',type=int,default=120);ap.add_argument('--workers',type=int,default=6);ap.add_argument('--seed',type=int,default=20261010);ap.add_argument('--dry-run',action='store_true');args=ap.parse_args()
 assert args.workers==6 and 1<=args.generations<=200 and args.batch>=20
 OUT.mkdir(parents=True,exist_ok=True)
 orig=load(BASE/'offspring.jsonl');ev=load(BASE/'evaluations.jsonl');assert len(orig)==len(ev)==1200
 allgenes={c['genome_hash']:c for c in orig};scores={}
 for r in ev:
  if r['status']=='EVALUATED_UNCERTIFIED':scores[r['genome_hash']]=score(r)
 # Gen2 remains immutable. Gen3 descendants get their own identifiers.
 seen=set(allgenes)
 for p in load(PARENTS):seen.add(digest((p['side'],p['chromosomes'])))
 archive=OUT/'candidates.jsonl';results=OUT/'evaluations.jsonl';state=OUT/'state.json'
 if state.exists():
  st=json.loads(state.read_text())
  assert st['seed']==args.seed and st['batch']==args.batch
  for c in load(archive):allgenes[c['genome_hash']]=c;seen.add(c['genome_hash'])
  for r in load(results):scores[r['genome_hash']]=score(r) if r['status']=='EVALUATED_UNCERTIFIED' else {}
 else:st={'seed':args.seed,'batch':args.batch,'generation':0,'stagnant':0,'best_novel_archive':0,'history':[],'status':'RUNNING_EXPLORATORY_UNCERTIFIED'}
 rng=random.Random(args.seed)
 # Deterministic restart via stored RNG state is required for exact resume.
 if st.get('rng_state'):
  def tuplify(x):return tuple(tuplify(y) for y in x) if isinstance(x,list) else x
  rng.setstate(tuplify(st['rng_state']))
 def niche_pool(side,h):
  pool=[c for c in allgenes.values() if c['side']==side and h in scores.get(c['genome_hash'],{})]
  pool.sort(key=lambda c:(scores[c['genome_hash']][h]['lcb'],scores[c['genome_hash']][h]['ev']),reverse=True)
  selected=[]
  for c in pool:
   if any(family_distance(c,s)==0 and signature(c)==signature(s) for s in selected):continue
   selected.append(c)
   if len(selected)>=25:break
  return selected
 for gen in range(st['generation']+1,args.generations+1):
  niches=[(side,h) for side in ('LONG','SHORT') for h in HORIZONS]
  active=[(s,h,niche_pool(s,h)) for s,h in niches if len(niche_pool(s,h))>=2]
  if not active:raise RuntimeError('No viable niches: investigate Gen2 data')
  # Round-robin across horizon/side niches; periodic immigrants from all Gen2, not only elites.
  children=[]
  for attempt in range(args.batch*200):
   if len(children)>=args.batch:break
   side,h,pool=active[len(children)%len(active)]
   if rng.random()<.2:
    candidates=[c for c in orig if c['side']==side]
    a=rng.choice(pool);b=rng.choice(candidates)
   else:a,b=rng.sample(pool,2)
   genes=mutate(a,b,rng);key=digest((side,genes))
   if key in seen:continue
   seen.add(key)
   children.append({'offspring_id':gen*100000+len(children)+1,'generation':gen,'side':side,'chromosomes':genes,'genome_hash':key,'parent_hashes':[a['genome_hash'],b['genome_hash']],'target_horizon':h})
  if len(children)<args.batch:raise RuntimeError('Novelty exhaustion; stopped rather than repeating clones')
  if args.dry_run:
   print('PREFLIGHT',gen,'active_niches',len(active),'generated',len(children));return
  append(archive,children)
  with concurrent.futures.ProcessPoolExecutor(max_workers=6,initializer=init_worker) as pool:
   evaluated=list(pool.map(evaluate,children,chunksize=1))
  append(results,evaluated)
  novel=0;qualified=0
  for c,r in zip(children,evaluated):
   allgenes[c['genome_hash']]=c
   s=score(r) if r['status']=='EVALUATED_UNCERTIFIED' else {}
   scores[c['genome_hash']]=s
   if s:qualified+=1
   h=c['target_horizon']
   if h in s:
    old=[x for x in allgenes.values() if x['genome_hash']!=c['genome_hash'] and x['side']==c['side'] and h in scores.get(x['genome_hash'],{})]
    old.sort(key=lambda x:scores[x['genome_hash']][h]['lcb'],reverse=True)
    if not any(family_distance(c,x)<.34 and scores[x['genome_hash']][h]['lcb']>=s[h]['lcb'] for x in old[:100]):novel+=1
  st['generation']=gen;st['stagnant']=0 if novel else st['stagnant']+1
  st['history'].append({'generation':gen,'offspring':len(children),'qualified_any_horizon':qualified,'novel_target_horizon':novel,'active_niches':len(active)})
  st['rng_state']=list(rng.getstate());state.write_text(json.dumps(st,indent=2))
  print('GEN',gen,'QUALIFIED',qualified,'NOVEL',novel,'NICHES',len(active),flush=True)
  if st['stagnant']>=8:
   st['status']='STOPPED_NO_NOVEL_TARGET_HORIZON_8_GENERATIONS';break
 else:st['status']='MAX_GENERATIONS_REACHED'
 state.write_text(json.dumps(st,indent=2))
if __name__=='__main__':main()
