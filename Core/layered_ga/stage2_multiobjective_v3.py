"""V3 candidate selection: two economic objectives, adverse-excursion frontier retained.

No scalarization and no arbitrary 2R cap. Each horizon is compared only to
the same horizon, preserving the complete horizon/MAE tradeoff for audit.
The evolutionary engine can use rank and crowding for tournament selection.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite, inf

@dataclass(frozen=True)
class Observation:
    candidate_id: str
    horizon: int
    ev_net: float
    lcb95: float
    mae_mean: float
    mae_tail5: float

def dominates(a: Observation, b: Observation) -> bool:
    if a.horizon != b.horizon:
        return False
    return (a.ev_net >= b.ev_net and a.lcb95 >= b.lcb95
            and (a.ev_net > b.ev_net or a.lcb95 > b.lcb95))

def extract(candidate_id, curve):
    return tuple(Observation(candidate_id, int(p["horizon"]), float(p["ev_net"]),
                             float(p["lcb95"]), float(p["mae_mean"]),
                             float(p.get("mae_tail5",float("nan"))))
                 for p in curve.points
                 if all(isfinite(float(p.get(k,float("nan"))))
                        for k in ("ev_net","lcb95","mae_mean")))

def nondominated_sort(items):
    """Stable NSGA-II fronts; deterministic candidate ID/horizon tie-breaking."""
    items=tuple(sorted(items,key=lambda x:(x.horizon,x.candidate_id)))
    counts=[0]*len(items)
    dominated=[[] for _ in items]
    for i,a in enumerate(items):
        for j,b in enumerate(items):
            if i==j:continue
            if dominates(a,b):dominated[i].append(j)
            elif dominates(b,a):counts[i]+=1
    fronts=[]
    current=[i for i,n in enumerate(counts) if n==0]
    while current:
        fronts.append(tuple(items[i] for i in current))
        following=[]
        for i in current:
            for j in dominated[i]:
                counts[j]-=1
                if counts[j]==0:following.append(j)
        current=sorted(set(following))
    return tuple(fronts)

def crowding_distance(front):
    """NSGA-II diversity in EV and confidence, without MAE-as-fitness."""
    front=tuple(front)
    distance={(p.candidate_id,p.horizon):0.0 for p in front}
    if len(front)<=2:
        return {key:inf for key in distance}
    for attr in ("ev_net","lcb95"):
        ordered=sorted(front,key=lambda p:(getattr(p,attr),p.candidate_id,p.horizon))
        distance[(ordered[0].candidate_id,ordered[0].horizon)]=inf
        distance[(ordered[-1].candidate_id,ordered[-1].horizon)]=inf
        width=getattr(ordered[-1],attr)-getattr(ordered[0],attr)
        if width>0:
            for i in range(1,len(ordered)-1):
                key=(ordered[i].candidate_id,ordered[i].horizon)
                distance[key]+=(getattr(ordered[i+1],attr)-getattr(ordered[i-1],attr))/width
    return distance

def rank_candidates(candidate_curves):
    """Per-horizon nondomination; best rank across 63 horizons is exploratory only.

    Final certification must independently validate stable windows, multiplicity,
    tail risk, and planted/null recovery; this rank cannot certify a candidate.
    """
    observations=tuple(p for cid,curve in candidate_curves for p in extract(cid,curve))
    fronts=nondominated_sort(observations)
    ranking={}
    for rank,front in enumerate(fronts):
        crowd=crowding_distance(front)
        for p in front:
            key=p.candidate_id
            candidate=(rank,-crowd[(key,p.horizon)],p.horizon)
            if key not in ranking or candidate<ranking[key]:ranking[key]=candidate
    return ranking,fronts
