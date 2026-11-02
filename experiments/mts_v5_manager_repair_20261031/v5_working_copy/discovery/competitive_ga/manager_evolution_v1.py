"""Manager-GA genome adapter for portfolio policy V2.
Fitness must come from chronological native portfolio replay, never proxies.
"""
from dataclasses import asdict,replace
import hashlib,json,random
from discovery.competitive_ga.manager_policy_v2 import Genes,decide

BOUNDS={
 "min_edge":(0.,.15),"risk_penalty":(0.,4.),
 "replace_margin":(0.,.15),"agreement_bonus":(0.,.05),
 "max_initial":(.01,.10),"max_total":(.10,.30),"min_cash":(0.,.5)
}

def identity(g):
    return hashlib.sha256(json.dumps(asdict(g),sort_keys=True).encode()).hexdigest()

def random_genome(rng):
    return Genes(**{k:rng.uniform(*v) for k,v in BOUNDS.items()})

def mutate(g,rng):
    d=asdict(g)
    key=rng.choice(tuple(BOUNDS))
    lo,hi=BOUNDS[key]
    d[key]=min(hi,max(lo,d[key]+rng.gauss(0,(hi-lo)*.12)))
    d["max_total"]=max(d["max_initial"],d["max_total"])
    return Genes(**d)

def crossover(a,b,rng):
    da,db=asdict(a),asdict(b)
    d={k:(da[k] if rng.random()<.5 else db[k]) for k in BOUNDS}
    d["max_total"]=max(d["max_initial"],d["max_total"])
    return Genes(**d)

def population(n=400,seed=7):
    rng=random.Random(seed)
    return [random_genome(rng) for _ in range(n)]

def pareto(scored):
    """Observed replay fitness: growth and negative drawdown; optional stability/EV."""
    from math import isfinite
    if not scored: return []
    dimensions=len(scored[0][1])
    if dimensions not in (2,4) or any(
        len(v)!=dimensions or any(not isinstance(x,(int,float)) or not isfinite(x) for x in v)
        for _,v in scored
    ):
        raise ValueError('consistent finite 2- or 4-objective replay fitness required')
    def dominates(a,b):
        return all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b))
    return [(g,v) for i,(g,v) in enumerate(scored)
            if not any(i!=j and dominates(w,v) for j,(_,w) in enumerate(scored))]

def offspring(scored,n=400,seed=8):
    if not scored:raise ValueError("missing replay results")
    rng=random.Random(seed)
    elite=[g for g,_ in pareto(scored)]
    if not elite:raise ValueError("no elite")
    result=list(elite[:n])
    while len(result)<n:
        if len(elite)>1 and rng.random()<.6:
            g=crossover(rng.choice(elite),rng.choice(elite),rng)
        else:g=mutate(rng.choice(elite),rng)
        result.append(g)
    return result
