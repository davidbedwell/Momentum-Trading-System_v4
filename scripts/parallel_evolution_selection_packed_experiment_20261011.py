"""Experimental packed-bit parent-pool screening; reference curation unchanged."""
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor
from scripts.evolution_active_dedup_fast_20261010 import curate
from scripts.run_evolution_v2_20261010 import qualify
from scripts.audit_evolution_domains_20261010 import valid
_CONTEXT=None

def packed_pool(side,h,genomes,results,domains,limit=20):
 options=[]
 for hash_,c in genomes.items():
  if c['side']!=side or not valid(c['chromosomes'],domains):continue
  r=results.get(hash_)
  if not r:continue
  q=qualify(r,h)
  if q and r.get('signal') and r['signal']['count']>=30:options.append((q,c,r))
 options.sort(key=lambda x:x[0],reverse=True)
 chosen=[];bits=[]
 for q,c,r in options:
  s=r['signal'];x=int.from_bytes(bytes.fromhex(s['bits']),'big');n=s['size'];count=s['count']
  unique=True
  for y,m,cy in bits:
   if n!=m:raise ValueError('Different observation universes')
   if min(count,cy)*100 < 85*max(count,cy):continue
   union=(x|y).bit_count()
   if ((x&y).bit_count()/union if union else 1.0)>=.85:unique=False;break
  if unique:chosen.append((q,c,r));bits.append((x,n,count))
  if len(chosen)>=limit:break
 return chosen

def _select(h):
 genomes,results,domains,side=_CONTEXT
 selected=curate(genomes,results,domains,(h,))
 allowed={(x['side'],x['horizon'],x['genome_hash']) for x in selected['active']}
 pool=[x for x in packed_pool(side,h,genomes,results,domains) if (side,h,x[1]['genome_hash']) in allowed]
 return h,pool

def parallel_niches(genomes,results,domains,horizons,workers=5,side='LONG'):
 global _CONTEXT
 hs=tuple(horizons)
 if not hs:return []
 _CONTEXT=(genomes,results,domains,side)
 try:
  with ProcessPoolExecutor(max_workers=min(workers,len(hs)),mp_context=mp.get_context('fork')) as ex:
   ordered=list(ex.map(_select,hs))
 finally:_CONTEXT=None
 return [(h,pool) for h,pool in ordered if len(pool)>=2]
