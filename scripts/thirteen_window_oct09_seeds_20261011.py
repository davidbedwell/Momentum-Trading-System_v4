"""Frozen October 9 Gen1/Gen2 parents plus 1,200 novel random genomes.
All fitness is recomputed by the window evaluator; no legacy scores imported.
"""
import hashlib,json,pathlib
from scripts.run_gen2_200_parent_parallel_20261010 import digest
from scripts.audit_evolution_domains_20261010 import valid
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'Research/Preparation/horizon_generational_20261010/parent_study/oct09_parent_seed_shortlist_20261011.json'
def load(domains,path=SOURCE):
 raw=pathlib.Path(path).read_bytes();bank=json.loads(raw)
 assert bank['count']==23 and bank['gen1_count']==8 and bank['gen2_count']==15
 assert bank['no_legacy_fitness_import'] is True
 seen=set();out=[]
 for r in bank['parents']:
  genes=r['chromosomes'];side=r['side'];key=digest((side,genes))
  if not valid(genes,domains):raise ValueError(f'OUT_OF_DOMAIN_LEGACY_PARENT {r["id"]}')
  if key!=r['genome_hash']:raise ValueError(f'LEGACY_HASH_MISMATCH {r["id"]}')
  if key in seen:raise ValueError(f'DUPLICATE_LEGACY_PARENT {r["id"]}')
  seen.add(key)
  out.append({'side':side,'chromosomes':genes,'genome_hash':key,'generation':0,'seed_origin':'OCT09_LEGACY','legacy_generation':r['generation'],'legacy_id':r['id'],'legacy_parent_ids':r.get('parent_ids'),'ancestor_legacy_ids':[{'generation':r['generation'],'id':r['id']}]})
 if {(x['legacy_generation'],x['legacy_id']) for x in out}.issuperset({(1,1660),(2,766)}) is False:raise ValueError('MANDATORY_PARENT_MISSING')
 return out,hashlib.sha256(raw).hexdigest()
def seed_population(rng,domains,random_size,fresh_fn,path=SOURCE):
 legacy,sha=load(domains,path);known={x['genome_hash'] for x in legacy}
 randoms=[]
 for _ in range(random_size):
  c=fresh_fn(rng,domains,'LONG',known)
  randoms.append(dict(c,generation=0,seed_origin='FRESH_RANDOM',ancestor_legacy_ids=[]))
 assert len(randoms)==random_size and len({x['genome_hash'] for x in legacy+randoms})==random_size+len(legacy)
 return randoms+legacy,sha
