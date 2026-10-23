"""Diversity-preserving GA5 population breeding; DEV79 research only."""
from collections import Counter
from dataclasses import replace
from ga5_chromosome_contract import mutate,crossover
from optimizer_v3 import NICHES

def gene_signature(g):
 return (g.entry_feature,g.hold_feature,g.exit_feature,g.regime_feature,g.sizing_feature,g.replace_feature)

def diversity(pop):
 c=Counter(g.niche for g in pop)
 return {'niche_counts':dict(c),'niches_represented':len(c),'distinct_gene_patterns':len({gene_signature(g) for g in pop}),'unique_chromosomes':len({g.identity() for g in pop})}

def breed_next(scored,rng,population,min_per_niche=None):
 if population<len(NICHES)*2:raise ValueError('At least two per niche required')
 minimum=min_per_niche if min_per_niche is not None else max(2,population//(len(NICHES)*5))
 if minimum*len(NICHES)>population:raise ValueError('Niche quota exceeds population')
 ranked=sorted(scored,key=lambda x:(-x[0],x[1].identity()))
 by={n:[g for _,g,_ in ranked if g.niche==n] for n in NICHES}
 if any(not v for v in by.values()):raise ValueError('Missing niche parent')
 out=[];seen=set();signatures=Counter()
 def add(g):
  if not g.valid() or g.identity() in seen:return False
  out.append(g);seen.add(g.identity());signatures[gene_signature(g)]+=1;return True
 # Preserve top specialist from each niche even when weak globally.
 for n in NICHES:add(by[n][0])
 # Guarantee each niche a viable exploratory population.
 for n in NICHES:
  tries=0
  while sum(g.niche==n for g in out)<minimum:
   tries+=1
   if tries>20000:raise RuntimeError('Niche diversity quota could not be filled')
   a=rng.choice(by[n][:max(1,len(by[n])//3)])
   b=rng.choice(by[n])
   child=mutate(crossover(a,b,rng),rng)
   add(child)
 # Fitness-ranked elites, with gene-signature diversity priority.
 elite_budget=min(population//5,population-len(out))
 elites=sorted(ranked,key=lambda x:(signatures[gene_signature(x[1])],-x[0],x[1].identity()))
 for _,g,_ in elites:
  if elite_budget<=0:break
  if add(g):elite_budget-=1
 # Mixed-niche crossover permitted; offspring inherit primary parent's origin.
 attempts=0
 while len(out)<population:
  attempts+=1
  if attempts>population*2000:raise RuntimeError('Could not create distinct offspring')
  n=min(NICHES,key=lambda x:sum(g.niche==x for g in out)) if rng.random()<.3 else rng.choice(NICHES)
  a=rng.choice(by[n][:max(1,len(by[n])//2)])
  b=rng.choice(ranked)[1]
  child=mutate(crossover(a,replace(b,niche=a.niche),rng),rng)
  if signatures[gene_signature(child)]>=max(3,population//20) and rng.random()<.9:continue
  add(child)
 stats=diversity(out)
 if stats['niches_represented']!=len(NICHES) or stats['unique_chromosomes']!=population:raise RuntimeError('Diversity invariant failed')
 return out,stats
