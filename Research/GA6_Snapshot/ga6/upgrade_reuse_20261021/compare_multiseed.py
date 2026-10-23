import json,random,collections,sys,statistics
sys.path.insert(0,'ga5_redesign')
from ga5_chromosome_contract import Genome
from ga6.breeder_portfolio_20261021 import breed_ga6 as current
from ga6.breeder_portfolio_diversity_20261021 import breed_ga6 as diversity
p='ga6/runs/ga6_ev_swing40_400_20261021/checkpoint_unified.json';d=json.load(open(p));scored=[(0.0,Genome(**g),{}) for g in d['members']];keys=('entry_feature','exit_feature','hold_feature','regime_feature','sizing_feature','replace_feature');rows=[]
for seed in range(20):
 for name,fn in [('production',current),('diversity_reference',diversity)]:
  children,meta=fn(scored,random.Random(seed+6100),400)
  patterns=collections.Counter(tuple(getattr(g,k) for k in keys) for g in children)
  niches=collections.Counter(g.niche for g in children)
  rows.append(dict(seed=seed,breeder=name,unique_genomes=len({g.identity() for g in children}),distinct_patterns=len(patterns),repeated_pattern_children=sum(v for v in patterns.values() if v>1),niche_min=min(niches.values()),niche_max=max(niches.values()),valid=all(g.valid() for g in children)))
summary={name:{k:dict(mean=statistics.mean(r[k] for r in rows if r['breeder']==name),minimum=min(r[k] for r in rows if r['breeder']==name),maximum=max(r[k] for r in rows if r['breeder']==name)) for k in ('distinct_patterns','repeated_pattern_children','niche_min')} for name in ('production','diversity_reference')}
assert all(r['unique_genomes']==400 and r['valid'] and r['niche_min']>=10 for r in rows)
result=dict(source_generation=d['generation'],seeds=20,rows=rows,summary=summary)
open('ga6/upgrade_reuse_20261021/multiseed_breeder_validation.json','w').write(json.dumps(result,indent=2));print(json.dumps({'generation':d['generation'],'summary':summary},indent=2))
