"""Small, serial GA with an internal chronological validation objective."""
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import random
import time
import numpy as np
from .execution import FAMILIES, Gene, Manager, replay
from .objective import HorizonMix, fit, predict, holding_predict, objective
from .benchmarks import selection_benchmark, primary_name


@dataclass(frozen=True)
class Candidate:
    genes: tuple
    manager: Manager
    mix: HorizonMix

    def record(self):
        return asdict(self)

    @property
    def id(self):
        return hashlib.sha256(json.dumps(self.record(),sort_keys=True).encode()).hexdigest()[:16]


def signals(p, candidate, models):
    if not candidate.genes:
        return np.empty((0,*p.close.shape))
    return np.stack([predict(p,g,m) for g,m in zip(candidate.genes,models)])


def funded(p, candidate, models, start, end, detail=True, omit=None):
    keep = [k for k in range(len(candidate.genes)) if k != omit]
    active = replace(candidate,genes=tuple(candidate.genes[k] for k in keep))
    models = [models[k] for k in keep]
    # The raw entry threshold belongs to predict; native engine sees net edge >0.
    genes = [replace(g,threshold=0.) for g in active.genes]
    hold = np.stack([holding_predict(p,g,m) for g,m in zip(active.genes,models)]) if active.genes else np.empty((0,*p.close.shape))
    return replay(p,genes,active.manager,start,end,detail,
                  signals(p,active,models),edge_mode=True,hold_signal=hold,horizon_mix=(active.mix.sessions,active.mix.weights))


def train_models(p, candidate, cutoff, cache):
    return [fit(p,g,candidate.mix,cutoff,label_cache=cache) for g in candidate.genes]


def seeds(horizons):
    mix = HorizonMix(tuple(horizons),tuple([1/len(horizons)]*len(horizons)))
    hold = round(sum(h*w for h,w in zip(mix.sessions,mix.weights)))
    manager = Manager(replacement=.0001)
    return [Candidate((),manager,mix),
            Candidate((Gene('trend',hold_sessions=hold),),manager,mix),
            Candidate((Gene('relative_strength','momentum','and',.2,hold_sessions=hold),),manager,mix),
            Candidate((Gene('volatility','recursive','and',.1,hold_sessions=hold),
                       Gene('momentum',hold_sessions=hold)),manager,mix)]


def mutate(parent, rng):
    w=np.array([rng.random()+.05 for _ in parent.mix.sessions]);w/=w.sum()
    mix=HorizonMix(parent.mix.sessions,tuple(w.tolist()))
    hold=round(sum(h*x for h,x in zip(mix.sessions,mix.weights)))
    genes=list(parent.genes) or [Gene(rng.choice(FAMILIES))]
    k=rng.randrange(len(genes));g=genes[k]
    genes[k]=replace(g,family=rng.choice(FAMILIES),second=rng.choice(FAMILIES),
                     op=rng.choice(['single','and','or']),threshold=rng.choice([-.2,.1,.3,.5]),
                     niche=rng.choice([-1,-1,0,1,2]),hold_sessions=hold,
                     hold_family=rng.choice(FAMILIES),exit_family=rng.choice(FAMILIES),
                     trailing=rng.choice([.03,.05,.08]),weight=rng.choice([.04,.06,.09]))
    if len(genes)<3 and rng.random()<.3:
        genes.append(Gene(rng.choice(FAMILIES),hold_sessions=hold))
    genes=[replace(g,hold_sessions=hold) for g in genes]
    manager=replace(parent.manager,slots=rng.choice([3,6,10]),reserve=rng.choice([.1,.3,.5]),
                    correlation=rng.choice([.6,.8,.95]),risk_cap=rng.choice([.004,.008,.012]),
                    replacement=rng.choice([.00005,.0001,.0003]),sector_cap=rng.choice([.20,.25,.30]))
    return Candidate(tuple(genes),manager,mix)


def search(p, year, generations=2, population=4, budget=30, seed=90079,
           horizons=(5,20,60,120), stop=lambda: False, progress=lambda row: None):
    """Select using internal forward half-year; external forward never enters here."""
    begin=time.monotonic()
    rng=random.Random(seed+year)
    calibration_end=f'{year-1}-07-01'
    train_end=f'{year}-01-01'
    passive=selection_benchmark(p,calibration_end,train_end)
    initial=seeds(horizons)
    population_rows=initial[:population]
    while len(population_rows)<population:
        population_rows.append(mutate(rng.choice(initial[1:]),rng))
    label_cache={}; evaluation_cache={}; journal=[]; rejected=[]
    best=None
    for generation in range(generations):
        ranked=[]
        for candidate in population_rows:
            if (stop() or time.monotonic()-begin>=budget) and best is not None:
                break
            if candidate.id not in evaluation_cache:
                models=train_models(p,candidate,calibration_end,label_cache)
                result=funded(p,candidate,models,calibration_end,train_end,detail=False)
                key=objective(result,passive)
                evaluation_cache[candidate.id]=(key,result,models)
            key,result,models=evaluation_cache[candidate.id]
            row=dict(generation=generation,id=candidate.id,candidate=candidate.record(),
                     label_cutoff=calibration_end,selection_start=calibration_end,selection_end=train_end,
                     phase='internal_validation_used_for_selection',benchmark=primary_name(p),metrics=result['metrics'],
                     elapsed_seconds=time.monotonic()-begin)
            journal.append(row)
            if not result['metrics']['feasible']:
                rejected.append(row)
            else:
                ranked.append((key,candidate))
                if best is None or key>best[0]:
                    best=(key,candidate)
            progress(row)
        if not ranked or stop() or time.monotonic()-begin>=budget:
            break
        ranked.sort(key=lambda x:x[0],reverse=True)
        elites=[c for _,c in ranked[:2]]
        population_rows=[initial[0],best[1]]
        while len(population_rows)<population:
            population_rows.append(mutate(rng.choice(elites),rng))
    if best is None:
        raise RuntimeError('No feasible candidate evaluated (cash control should be feasible)')
    selected=best[1]
    # Refit ONLY the selected genome after selection; no tuning on external forward.
    frozen_models=train_models(p,selected,train_end,label_cache)
    return selected,frozen_models,dict(journal=journal,rejected_risk=rejected,
               calibration_end=calibration_end,selection_start=calibration_end,selection_end=train_end,
               selected_id=selected.id,elapsed_seconds=time.monotonic()-begin,
               selection_metrics=evaluation_cache[selected.id][1]['metrics'],
               stop_reason='STOP' if stop() else 'budget' if time.monotonic()-begin>=budget else 'generation_cap')
