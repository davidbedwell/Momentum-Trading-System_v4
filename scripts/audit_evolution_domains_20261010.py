"""Audited, frozen mutation domain: categorical enums and bounded numeric values.
Historical genomes are immutable; this governs newly generated descendants only.
"""
import json,pathlib,collections,hashlib
from scripts.evolution_safety_20261010 import domain_catalog
ROOT=pathlib.Path(__file__).resolve().parents[1]
FILES={
 'gen1_parents':ROOT/'Research/Governance/GEN2_200_PARENT_FREEZE_20261009/frozen_200_parent_genomes.jsonl',
 'gen2_children':ROOT/'Research/Runs/gen2-200-parent-20261010/offspring.jsonl',
 'gen3_pilot':ROOT/'Research/Runs/gen3-adaptive-evolution/candidates.jsonl',
}
NUMERIC_KEYS=('threshold','quantile','severity')
def schema():
 c=domain_catalog();out={}
 for family,genes in c.items():
  out[family]={}
  for key,values in genes.items():
   numeric=any(s in key for s in NUMERIC_KEYS) and all(type(v) in (float,int) for v in values)
   if numeric:
    lo=min(values);hi=max(values)
    # Numerical thresholds represent fractions or quantiles, never unbounded prices.
    if not (0<=lo<hi<=1):raise ValueError((family,key,lo,hi))
    out[family][key]={'kind':'continuous','min':lo,'max':hi,'precision':3,'original_grid':list(values)}
   else:out[family][key]={'kind':'categorical','values':list(values)}
 return out
def valid(genes,domains):
 if not genes or len({f for f,_ in genes})!=len(genes):return False
 for family,g in genes:
  spec=domains.get(family)
  if not spec or set(g)!=set(spec):return False
  for key,v in g.items():
   s=spec[key]
   if s['kind']=='categorical':
    if v not in s['values']:return False
   elif type(v) not in (int,float) or not s['min']<=v<=s['max']:return False
 return True
def mutate(genes,rng,domains):
 import copy
 out=copy.deepcopy(genes)
 candidates=[(i,key) for i,(fam,g) in enumerate(out) for key in g]
 rng.shuffle(candidates)
 for i,key in candidates:
  fam,g=out[i];s=domains[fam][key];old=g[key]
  if s['kind']=='categorical':
   choices=[v for v in s['values'] if v!=old]
   if not choices:continue
   g[key]=rng.choice(choices)
  else:
   step=rng.choice((.01,.025,.05))
   g[key]=round(max(s['min'],min(s['max'],old+rng.choice((-1,1))*step)),s['precision'])
   if g[key]==old:continue
  if valid(out,domains):return out
  g[key]=old
 return out
def audit():
 domains=schema();report={'domain_policy':'numeric within min/max of certified original grid, precision .001; categorical exact','historical_genomes_unchanged':True,'files':{},'domains':domains}
 for name,path in FILES.items():
  rows=[json.loads(x) for x in path.open()];bad=collections.Counter();affected=0
  for row in rows:
   if valid(row['chromosomes'],domains):continue
   affected+=1
   for fam,g in row['chromosomes']:
    for k,v in g.items():
     s=domains[fam][k]
     if (s['kind']=='categorical' and v not in s['values']) or (s['kind']=='continuous' and not s['min']<=v<=s['max']):bad[(fam,k,str(v))]+=1
  report['files'][name]={'count':len(rows),'outside_proposed_bounds':affected,'violations':[{'family':f,'key':k,'value':v,'count':n} for (f,k,v),n in bad.most_common()],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 return report
if __name__=='__main__':
 report=audit();out=ROOT/'Research/Governance/EVOLUTION_MUTATION_DOMAIN_AUDIT_20261010.json';out.write_text(json.dumps(report,indent=2));print(json.dumps({k:{'count':v['count'],'outside_proposed_bounds':v['outside_proposed_bounds'],'violations':v['violations'][:5]} for k,v in report['files'].items()},indent=2))
