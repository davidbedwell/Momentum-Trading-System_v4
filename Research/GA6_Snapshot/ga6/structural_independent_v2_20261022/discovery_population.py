"""Versioned GA6 population proposal using existing Genome evaluator contract.
No claims that separate boolean catalog expressions execute in the legacy evaluator.
"""
from dataclasses import replace
from collections import defaultdict
from scipy.stats import qmc
from ga5_chromosome_contract import FEATURES,mutate,crossover
from ga6.structural_independent_v2_20261022.discovery_allocation import allocate
from ga5_redesign.optimizer_v3 import NICHES
FEATURE_FIELDS=('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature')
THRESH_FIELDS=('entry_threshold','hold_threshold','exit_threshold','regime_threshold','replace_threshold')

def sobol_variant(parent,seed,index):
    # Scrambled Sobol over independent feature choices and five thresholds.
    vector=qmc.Sobol(d=11,scramble=True,seed=seed).random_base2(m=max(1,(index+1).bit_length()))[index]
    names=sorted(FEATURES)
    updates={f:names[min(len(names)-1,int(vector[i]*len(names)))] for i,f in enumerate(FEATURE_FIELDS)}
    updates.update({f:round(2*vector[6+i]-1,6) for i,f in enumerate(THRESH_FIELDS)})
    child=replace(parent,**updates)
    assert child.valid()
    return child

def propose(scored,rng,population=400,generation=0,observations=None):
    """Produce all four activity tracks, protect 13 niches, and return provenance.
    Scored tuples: (fitness, Genome, result). Results are not reinterpreted.
    """
    if not scored:raise ValueError('No evaluated parents')
    by_niche=defaultdict(list)
    for fitness,g,result in sorted(scored,key=lambda row:-row[0]):by_niche[g.niche].append(g)
    if any(not by_niche[n] for n in NICHES):raise ValueError('Niche missing from parent population')
    budgets=allocate(observations,population,generation)
    out=[];seen=set();provenance=[]
    def add(g,activity):
        if g.valid() and g.identity() not in seen:
            out.append(g);seen.add(g.identity());provenance.append(activity);return True
        return False
    # Retain at least ten distinct best-scored niche candidates when present.
    for niche in NICHES:
        for g in by_niche[niche][:10]:add(g,'protected_niche')
    # Existing evaluated elites are carried independently of exploratory allocation.
    remaining=population-len(out)
    if remaining<0:raise ValueError('Elite archive exceeds population')
    targets=allocate(observations,remaining,generation) if remaining>=4 else dict.fromkeys(budgets,0)
    for activity,target in targets.items():
        count=0;attempts=0
        while count<target and len(out)<population:
            attempts+=1
            if attempts>target*150+500:raise RuntimeError('Unable to generate novel population')
            niche=NICHES[(len(out)+attempts+generation)%len(NICHES)]
            pool=by_niche[niche][:min(20,len(by_niche[niche]))]
            parent=rng.choice(pool)
            if activity in ('new_structures','sobol_refinement'):
                child=sobol_variant(parent,rng.getrandbits(32),attempts+count)
                if activity=='sobol_refinement':
                    child=replace(child,**{f:getattr(parent,f) for f in FEATURE_FIELDS})
            elif activity=='evolution':
                child=mutate(crossover(parent,rng.choice(pool),rng),rng)
            else:
                child=mutate(parent,rng)
                for _ in range(2):child=mutate(child,rng)
            if add(child,activity):count+=1
    while len(out)<population:
        parent=rng.choice(by_niche[rng.choice(NICHES)])
        add(sobol_variant(parent,rng.getrandbits(32),len(out)),'fill')
    return out,{'origins':provenance,'budgets':budgets,'actual':{k:provenance.count(k) for k in set(provenance)},'niches':len({g.niche for g in out}),'protected':{n:sum(g.niche==n and g.identity() in {x.identity() for x in by_niche[n][:10]} for g in out) for n in NICHES}}
