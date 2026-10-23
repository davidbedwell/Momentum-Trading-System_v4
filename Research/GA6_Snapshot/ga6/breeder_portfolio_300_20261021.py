"""GA6 300-population breeder: 10 per niche, 120 global, 50 novelty."""
from dataclasses import replace
from ga5_chromosome_contract import mutate,crossover
from optimizer_v3 import NICHES

def breed_ga6(scored,rng,population,niche_ranks=None):
 if population!=300: raise ValueError('This breeder requires 300 members')
 ranked=list(scored)
 by={n:[g for _,g,_ in ranked if g.niche==n] for n in NICHES}
 if any(not v for v in by.values()):raise ValueError('Missing niche')
 out=[];seen=set();patterns=set()
 def signature(g):return (g.entry_feature,g.exit_feature,g.hold_feature,g.regime_feature,g.sizing_feature,g.replace_feature)
 def add(g,novel=False):
  if not g.valid() or g.identity() in seen:return False
  if novel and signature(g) in patterns:return False
  seen.add(g.identity());patterns.add(signature(g));out.append(g);return True
 def spawn(a,b,n):return mutate(crossover(a,replace(b,niche=n),rng),rng)
 elite=[g for _,g,_ in ranked[:75]]
 for n in NICHES:
  add(by[n][0]);tries=0
  while sum(g.niche==n for g in out)<10:
   tries+=1
   if tries>20000:raise RuntimeError('Niche quota exhausted '+n)
   a=rng.choice(by[n][:max(1,len(by[n])//2)]);b=rng.choice(elite)
   add(spawn(a,b,n))
 tries=0
 while len(out)<250:
  tries+=1
  if tries>100000:raise RuntimeError('Global breeding exhausted')
  a=rng.choice(elite);b=rng.choice(ranked)[1];add(spawn(a,b,rng.choice(NICHES)))
 tries=0
 while len(out)<300:
  tries+=1
  if tries>200000:raise RuntimeError('Novelty exploration exhausted')
  n=rng.choice(NICHES)
  a=rng.choice(by[n]);b=rng.choice(ranked)[1]
  add(spawn(a,b,n),novel=True)
 return out,{'unique_chromosomes':len(seen),'distinct_gene_patterns':len(patterns),'niches_represented':len({g.niche for g in out}),'selection':'ga6_300_niche_global_novelty'}
