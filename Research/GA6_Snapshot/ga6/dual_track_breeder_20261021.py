"""Dual-track Pareto breeding, isolated from GA6 production.
No production code or checkpoint mutations.
"""
from collections import Counter
from dataclasses import replace
from ga5_chromosome_contract import mutate,crossover
from ga5_redesign.optimizer_v3 import NICHES
from ga6.pareto_library_20261021 import rank
from ga6.dual_track_research_20261021 import rank_tracks

def breed_dual_track(scored,rng,population,selector='pareto'):
    if population<4*len(NICHES):raise ValueError('Population too small for protected tracks')
    if selector not in ('pareto','weighted'):raise ValueError('Invalid selector')
    rows=[{'chromosome_id':g.identity(),'origin_niche':g.niche,'result':result} for _,g,result in scored]
    tracks=rank_tracks(rows,NICHES)
    lookup={g.identity():g for _,g,_ in scored}
    def select(items):
        if selector=='pareto':
            return rank(items)
        return sorted(items,key=lambda x:(-x['metrics']['score'],x['id']))
    general=[lookup[x['id']] for x in select(tracks['generalist'])]
    specialists={n:[lookup[x['id']] for x in select(items)] for n,items in tracks['specialists'].items()}
    # Each niche has a protected specialist quota; only assigned-niche results qualify.
    # No eligible specialists -> fallback to that niche's current genomes, flagged as unproven.
    existing={n:[g for _,g,_ in scored if g.niche==n] for n in NICHES}
    if any(not v for v in existing.values()):raise ValueError('Missing niche in source population')
    parents={n:(specialists[n] or existing[n]) for n in NICHES}
    general=general or [g for _,g,_ in sorted(scored,key=lambda x:-x[0])]
    out=[];seen=set()
    def add(g):
        if g.valid() and g.identity() not in seen:
            out.append(g);seen.add(g.identity())
    # Preserve two distinct specialists in each niche where possible.
    for n in NICHES:
        for g in parents[n][:2]:add(g)
    for g in general[:max(1,population//10)]:add(g)
    attempts=0
    while len(out)<population:
        attempts+=1
        if attempts>population*1000:raise RuntimeError('Genome novelty exhausted')
        n=min(NICHES,key=lambda x:sum(g.niche==x for g in out)) if rng.random()<.6 else rng.choice(NICHES)
        specialist=rng.choice(parents[n][:max(1,min(8,len(parents[n])))])
        if rng.random()<.75:
            other=rng.choice(parents[n][:max(1,min(8,len(parents[n])))])
        else:
            other=replace(rng.choice(general[:max(1,min(20,len(general)))]),niche=n)
        add(mutate(crossover(specialist,other,rng),rng))
    return out,{'selector':selector,'protected_niches':len(NICHES),
                'specialist_eligible':{n:len(specialists[n]) for n in NICHES},
                'fallback_niches':[n for n in NICHES if not specialists[n]],
                'population':len(out)}
