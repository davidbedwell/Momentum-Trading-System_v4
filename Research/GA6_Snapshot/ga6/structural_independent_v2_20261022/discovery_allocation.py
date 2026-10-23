"""GA6 adaptive discovery allocation. Pure scheduling logic; no production mutation.
All activities run concurrently. Rewards are validated novelty per compute, not champion score.
"""
from dataclasses import dataclass
import math
ACTIVITIES=('new_structures','sobol_refinement','evolution','challengers')
BASE=(.45,.20,.25,.10)
@dataclass(frozen=True)
class Observation:
    trials:int
    novel:int
    compute_seconds:float
    uncertainty:float=0.0
    stable_fraction:float=1.0
    diverse_fraction:float=1.0

def allocate(observations=None, population=400, generation=0, refresh=5, cap=.60, floor=.05):
    if population<4 or cap<.25 or floor<0 or floor*4>1:raise ValueError('Invalid allocation constraints')
    weights=list(BASE)
    if observations and generation>=refresh and generation%refresh==0:
        signals=[]
        for i,name in enumerate(ACTIVITIES):
            o=observations.get(name)
            if o is None or o.trials<5 or o.compute_seconds<=0:
                signals.append(BASE[i]);continue
            rate=o.novel/max(o.compute_seconds,1e-6)
            evidence=o.trials/(o.trials+20)
            quality=max(0,min(1,o.stable_fraction))*max(0,min(1,o.diverse_fraction))
            signals.append(BASE[i]*(1-evidence)+evidence*(rate*quality+max(0,o.uncertainty)*.01))
        total=sum(signals)
        if total>0:weights=[v/total for v in signals]
    # Projection onto capped simplex; ensures no activity starves or monopolizes budget.
    for _ in range(30):
        bounded=[max(floor,min(cap,v)) for v in weights]
        delta=1-sum(bounded)
        if abs(delta)<1e-10:break
        free=[i for i,v in enumerate(bounded) if (v<cap-1e-10 if delta>0 else v>floor+1e-10)]
        if not free:break
        weights=bounded
        for i in free:weights[i]+=delta/len(free)
    weights=[max(floor,min(cap,v)) for v in weights]
    if abs(sum(weights)-1)>1e-7:raise AssertionError('Allocation not normalized')
    exact=[v*population for v in weights]
    counts=[math.floor(v) for v in exact]
    for i in sorted(range(4),key=lambda i:(-(exact[i]-counts[i]),i))[:population-sum(counts)]:counts[i]+=1
    if sum(counts)!=population:raise AssertionError('Population mismatch')
    return dict(zip(ACTIVITIES,counts))
