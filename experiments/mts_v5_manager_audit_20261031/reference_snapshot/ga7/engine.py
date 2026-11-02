"""Standalone GA7 genome grammar and evolutionary selection."""
from dataclasses import dataclass, asdict, replace
from hashlib import sha256
import json
import random

FAMILIES = ("momentum", "breakout", "trend", "mean_reversion", "volatility", "volume_liquidity", "relative_cross_sectional", "market_regime_structure")
EXITS = ("signal_decay", "volatility", "reversal")

@dataclass(frozen=True)
class Genome:
    family: str
    feature_a: str
    feature_b: str
    operator: str
    threshold_a: float
    threshold_b: float
    entry_pct: float
    capacity: int
    exit_rule: str
    stop_pct: float

    def identity(self):
        return sha256(json.dumps(asdict(self), sort_keys=True).encode()).hexdigest()[:20]

def validate(g, features):
    assert g.family in FAMILIES
    assert g.feature_a in features[g.family] and g.feature_b in features[g.family]
    assert g.operator in ("AND", "OR")
    assert -1 <= g.threshold_a <= 1 and -1 <= g.threshold_b <= 1
    assert .03 <= g.entry_pct <= .10
    assert 1 <= g.capacity <= 10 and g.exit_rule in EXITS
    assert .01 <= g.stop_pct <= .02
    return g

def random_genome(rng, features, family=None):
    family = family or rng.choice(FAMILIES)
    a, b = rng.sample(tuple(features[family]), 2)
    return validate(Genome(family, a, b, rng.choice(("AND", "OR")), rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(.03, .10), rng.randint(1, 10), rng.choice(EXITS), rng.uniform(.01, .02)), features)

def mutate(g, rng, features):
    key = rng.choice(tuple(asdict(g)))
    if key == "family":
        return random_genome(rng, features)
    options = {
        "feature_a": lambda: rng.choice(tuple(features[g.family])),
        "feature_b": lambda: rng.choice(tuple(features[g.family])),
        "operator": lambda: rng.choice(("AND", "OR")),
        "threshold_a": lambda: rng.uniform(-1, 1),
        "threshold_b": lambda: rng.uniform(-1, 1),
        "entry_pct": lambda: rng.uniform(.03, .10),
        "capacity": lambda: rng.randint(1, 10),
        "exit_rule": lambda: rng.choice(EXITS),
        "stop_pct": lambda: rng.uniform(.01, .02),
    }
    return validate(replace(g, **{key: options[key]()}), features)

def crossover(a, b, rng, features):
    if a.family != b.family:
        return mutate(rng.choice((a, b)), rng, features)
    return validate(Genome(**{k: getattr(rng.choice((a, b)), k) for k in asdict(a)}), features)

def breeding_metrics(m):
    """Research objectives: conservative R expectancy, stop proximity, novelty."""
    return (float(m.get('conservative_ev_r', -1)),
            -float(m.get('mae_stop_ratio', 10)),
            float(m.get('behavioral_diversity', 0)))

def dominates(a, b):
    av, bv = breeding_metrics(a), breeding_metrics(b)
    return all(x >= y for x,y in zip(av,bv)) and any(x > y for x,y in zip(av,bv))

def breeding_eligible(m):
    # No individual-CAGR or MDD gate; those are portfolio-level diagnostics.
    return m.get('trades',0) >= 5 and m.get('conservative_ev_r',-1) > 0

def add_behavioral_diversity(scored):
    """Jaccard novelty of trade-entry signatures; deterministic and population-relative."""
    sets = [set(m.get('entry_signature', ())) for _,m in scored]
    for i,(_,m) in enumerate(scored):
        others = [(1-len(sets[i]&sets[j])/len(sets[i]|sets[j])) if sets[i] and sets[j] else 0. for j in range(len(sets)) if j!=i]
        m['behavioral_diversity'] = sum(sorted(others)[:5])/min(5,len(others)) if others else 0.
    return scored

def pareto_fronts(scored):
    remaining, result = list(range(len(scored))), []
    while remaining:
        front = [i for i in remaining if not any(dominates(scored[j][1], scored[i][1]) for j in remaining if j != i)]
        if not front:
            raise RuntimeError("Non-dominated sorting failed")
        result.append(front)
        chosen = set(front)
        remaining = [i for i in remaining if i not in chosen]
    return result

def niche_population_groups(niche_ids):
    return tuple(niche_ids) + ('NON_NICHE',)

def breed_by_group(scored_by_group, rng, features, size_per_group):
    return {key: next_population(rows, rng, features, size_per_group) for key,rows in scored_by_group.items()}

def next_population(scored, rng, features, size=300):
    if len(scored) < 2:
        raise ValueError("Need at least two scored chromosomes")
    scored = add_behavioral_diversity(scored)
    # Discovery is NOT certification: trade activity and aggregate EV guide
    # breeding; conservative positive EV is a promotion diagnostic only.
    active=[(g,m) for g,m in scored if m.get('trades',0)>=5]
    def quality(item):
        g,m=item
        return (float(m.get('ev_r',-1))-0.20*max(0.,float(m.get('mae_stop_ratio',0))-1)
                -0.05*float(m.get('fold_ev_spread',0)),
                float(m.get('conservative_ev_r',-1)),m.get('trades',0))
    ranked=sorted(active,key=quality,reverse=True)
    parents=[g for g,m in ranked[:max(8,size//4)]]
    output,seen=[],set()
    def add(g):
        if g.identity() not in seen:
            seen.add(g.identity());output.append(g)
    for g in parents[:max(1,size//10)]:add(g)
    for family in FAMILIES:
        if not any(g.family==family for g in output):
            add(random_genome(rng,features,family))
    attempts=0
    while len(output)<size:
        attempts+=1
        if attempts>size*100:raise RuntimeError('Population diversity exhausted')
        if rng.random()<.20 or not parents:
            child=random_genome(rng,features)
        else:
            child=mutate(crossover(rng.choice(parents),rng.choice(parents),rng,features),rng,features)
        add(child)
    return output
