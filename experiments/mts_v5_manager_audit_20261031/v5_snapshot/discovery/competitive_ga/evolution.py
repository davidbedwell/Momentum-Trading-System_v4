"""Competitive portfolio GA evolutionary mechanics. No synthetic portfolio fitness."""
from dataclasses import dataclass, asdict
import random, json, hashlib

FEATURES=('trend','momentum','volatility','breadth','niche_strength','niche_distance','signal_confidence','chromosome_reliability','correlation','holding_advantage')
@dataclass(frozen=True)
class Genome:
    weights: tuple
    entry_threshold: float
    replacement_margin: float
    target_weight: float
    niche_enabled: bool
    regime_enabled: bool

    def __post_init__(self):
        if len(self.weights)!=len(FEATURES) or any(not -2<=x<=2 for x in self.weights):raise ValueError('weights')
        if not 0<=self.entry_threshold<=2 or not 0<=self.replacement_margin<=1 or not 0<self.target_weight<=.10:raise ValueError('bounds')
    @property
    def identity(self):return hashlib.sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()

def new(rng):
    return Genome(tuple(round(rng.uniform(-1,1),5) for _ in FEATURES),round(rng.uniform(0,1),5),round(rng.uniform(0,.25),5),round(rng.uniform(.02,.1),5),rng.choice([True,False]),rng.choice([True,False]))

def mutate(g,rng):
    w=list(g.weights);i=rng.randrange(len(w));w[i]=round(max(-2,min(2,w[i]+rng.gauss(0,.25))),5)
    return Genome(tuple(w),max(0,min(2,g.entry_threshold+rng.gauss(0,.08))),max(0,min(1,g.replacement_margin+rng.gauss(0,.03))),max(.001,min(.10,g.target_weight+rng.gauss(0,.01))),g.niche_enabled if rng.random()>.1 else not g.niche_enabled,g.regime_enabled if rng.random()>.1 else not g.regime_enabled)

def crossover(a,b,rng):
    return Genome(tuple(x if rng.random()<.5 else y for x,y in zip(a.weights,b.weights)),a.entry_threshold if rng.random()<.5 else b.entry_threshold,a.replacement_margin if rng.random()<.5 else b.replacement_margin,a.target_weight if rng.random()<.5 else b.target_weight,a.niche_enabled if rng.random()<.5 else b.niche_enabled,a.regime_enabled if rng.random()<.5 else b.regime_enabled)

def initial_population(n=400,seed=7):
    rng=random.Random(seed);p=[];seen=set()
    while len(p)<n:
        g=new(rng)
        if g.identity not in seen:p.append(g);seen.add(g.identity)
    return p

def dominates(a,b):
    """All objectives are higher-is-better; a and b are evaluated vectors."""
    return all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b))

def pareto_front(scored):
    """scored: [(genome, (excess_wealth, -drawdown, fold_stability)), ...]."""
    return [(g,v) for i,(g,v) in enumerate(scored) if not any(j!=i and dominates(w,v) for j,(_,w) in enumerate(scored))]

def next_generation(scored,n=400,seed=7):
    """Requires externally supplied REAL full-portfolio replay fitness vectors."""
    if not scored:raise ValueError('missing real portfolio fitness')
    if any(len(v)!=3 for _,v in scored):raise ValueError('invalid fitness vector')
    rng=random.Random(seed);front=pareto_front(scored)
    pool=[g for g,_ in front] or [scored[0][0]]
    # Keep diverse frontier and select parents by tournament over externally evaluated objectives.
    result=[];seen=set()
    for g in pool:
        if g.identity not in seen and len(result)<n:result.append(g);seen.add(g.identity)
    attempts=0
    while len(result)<n and attempts<n*100:
        attempts+=1
        if rng.random()<.05:g=new(rng)
        elif rng.random()<.60 and len(pool)>1:g=crossover(rng.choice(pool),rng.choice(pool),rng)
        else:g=mutate(rng.choice(pool),rng)
        if g.identity not in seen:result.append(g);seen.add(g.identity)
    if len(result)<n:raise RuntimeError('insufficient unique offspring')
    return result
