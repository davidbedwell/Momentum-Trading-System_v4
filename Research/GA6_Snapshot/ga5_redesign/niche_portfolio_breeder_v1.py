"""Research-only niche-isolated portfolio breeder. Never crosses niche boundaries."""
from collections import Counter
from ga5_chromosome_contract import mutate,crossover
from optimizer_v3 import NICHES
from niche_portfolio_pareto_v1 import niche_portfolio_selection
from evolution_controls import diversity,gene_signature

def breed_niche_portfolio(scored,rng,population):
    if population<2*len(NICHES):raise ValueError('Insufficient population')
    ranked=niche_portfolio_selection(scored)
    if any(n not in ranked for n in NICHES):raise ValueError('Missing valid niche portfolio evaluations')
    sizes={n:population//len(NICHES)+(i<population%len(NICHES)) for i,n in enumerate(NICHES)}
    out=[];seen=set();counts=Counter()
    def add(g):
        if not g.valid() or g.identity() in seen:return False
        out.append(g);seen.add(g.identity());counts[g.niche]+=1;return True
    for niche in NICHES:
        pool=[g for _,g,_ in ranked[niche]]
        add(pool[0])
        elites=max(1,sizes[niche]//5)
        for g in pool[1:elites]:add(g)
        attempts=0
        while counts[niche]<sizes[niche]:
            attempts+=1
            if attempts>sizes[niche]*3000:raise RuntimeError('Niche offspring diversity exhausted: '+niche)
            top=pool[:max(2,len(pool)//2)]
            a=rng.choice(top)
            b=rng.choice(top)
            child=mutate(crossover(a,b,rng),rng)
            if child.niche!=niche:raise AssertionError('Niche lineage changed')
            add(child)
    stats=diversity(out)
    if stats['unique_chromosomes']!=population or stats['niches_represented']!=len(NICHES):raise AssertionError('Breeding invariant failed')
    stats.update(selection='within_niche_portfolio_cagr_mdd',cross_niche_mating=False,niche_counts=dict(counts))
    return out,stats
