"""GA6 EV-ranked cross-niche breeder with protected niche quotas."""
from collections import Counter
from dataclasses import replace
from ga5_chromosome_contract import mutate,crossover
from optimizer_v3 import NICHES

def breed_ga6(scored,rng,population,niche_ranks=None):
 if population<2*len(NICHES):raise ValueError('Insufficient niche breadth')
 ranked=list(scored) # Pareto fronts and crowding already ranked by caller
 by={n:[x[1] for x in ranked if x[1].niche==n] for n in NICHES}
 if niche_ranks is not None:
  genome_by_id={g.identity():g for _,g,_ in scored}
  for n in NICHES:
   specialists=[replace(genome_by_id[gid],niche=n) for gid,_ in niche_ranks[n][:max(1,population//len(NICHES))] if gid in genome_by_id]
   by[n]=specialists+by[n]
 if any(not x for x in by.values()):raise ValueError('Missing niche')
 out=[];seen=set()
 def add(g):
  if g.valid() and g.identity() not in seen:
   seen.add(g.identity());out.append(g)
 # Protect ten distinct candidates per niche, retaining ranked specialists.
 for n in NICHES:
  for g in by[n][:10]:add(g)
 elite=[x[1] for x in ranked[:max(13,population//4)]]
 attempts=0
 # Reserve 50 slots for broad novelty by generating mutated niche seeds.
 novelty_target=min(50,max(0,population-len(out)))
 novelty_attempts=0
 while len(out)<population and novelty_target>0 and novelty_attempts<population*200:
  novelty_attempts+=1
  n=rng.choice(NICHES)
  candidate=mutate(rng.choice(by[n]),rng)
  before=len(out);add(candidate)
  if len(out)>before:novelty_target-=1
 while len(out)<population:
  attempts+=1
  if attempts>population*1000:raise RuntimeError('Novel genome exhaustion')
  n=min(NICHES,key=lambda k:sum(g.niche==k for g in out)) if rng.random()<.35 else rng.choice(NICHES)
  a=rng.choice(by[n][:max(1,len(by[n])//2)])
  b=rng.choice(elite)
  child=mutate(crossover(a,replace(b,niche=n),rng),rng)
  add(child)
 return out,{'unique_chromosomes':len(seen),'niches_represented':len({g.niche for g in out}),'cross_niche_donors':True,'selection':'ga6_niche_ev' if niche_ranks is not None else 'ga6_ev'}
