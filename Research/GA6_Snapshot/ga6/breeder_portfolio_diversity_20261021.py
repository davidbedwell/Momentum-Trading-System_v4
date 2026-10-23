"""GA6 v2: niche quotas and gene-pattern diversity, EV-ranked parents."""
from collections import Counter
from dataclasses import replace
from ga5_chromosome_contract import mutate,crossover
from optimizer_v3 import NICHES

def pattern(g):
 return (g.entry_feature,g.exit_feature,g.hold_feature,g.regime_feature,g.sizing_feature,g.replace_feature)

def breed_ga6(scored,rng,population,niche_ranks=None):
 if population<2*len(NICHES):raise ValueError('Insufficient population')
 by={n:[g for _,g,_ in scored if g.niche==n] for n in NICHES}
 if any(not by[n] for n in NICHES):raise ValueError('Missing niche')
 out=[];seen=set();patterns=Counter();counts=Counter()
 def add(g):
  if not g.valid() or g.identity() in seen:return False
  seen.add(g.identity());out.append(g);patterns[pattern(g)]+=1;counts[g.niche]+=1
  return True
 quota=max(2,population//(2*len(NICHES)))
 # Protect a substantial research allocation per niche, rather than one elite.
 for n in NICHES:
  add(by[n][0]);attempts=0
  while counts[n]<quota:
   attempts+=1
   if attempts>population*500:raise RuntimeError('Niche quota novelty exhaustion')
   a=rng.choice(by[n][:max(1,len(by[n])//2)])
   b=rng.choice(by[n][:max(1,len(by[n])//2)]) if rng.random()<.65 else rng.choice([g for _,g,_ in scored[:max(13,population//4)]])
   add(mutate(crossover(a,replace(b,niche=n),rng),rng))
 elites=[g for _,g,_ in scored[:max(13,population//4)]]
 attempts=0
 while len(out)<population:
  attempts+=1
  if attempts>population*1500:raise RuntimeError('Novel genome exhaustion')
  n=min(NICHES,key=lambda k:counts[k]) if rng.random()<.35 else rng.choice(NICHES)
  a=rng.choice(by[n][:max(1,len(by[n])//2)])
  b=rng.choice(elites)
  child=mutate(crossover(a,replace(b,niche=n),rng),rng)
  # Resist pattern collapse, but do not forbid repeated patterns.
  if patterns[pattern(child)]>=2 and attempts%5!=0:continue
  add(child)
 return out,{'unique_chromosomes':len(seen),'distinct_gene_patterns':len(patterns),'niches_represented':len(counts),'minimum_niche_population':min(counts.values()),'quota':quota,'cross_niche_donors':True,'selection':'ga6_diversity_v2'}
