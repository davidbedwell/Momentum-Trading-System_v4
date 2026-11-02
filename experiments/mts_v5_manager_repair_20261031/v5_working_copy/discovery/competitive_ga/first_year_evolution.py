"""Bounded manager evolution using observed causal portfolio replay only.

Factories must create fresh native producers, shadow books, and day streams on
EACH call. Validation is replayed once with the frozen training winner. This is
an integration API, not certification of caller data or native feature parity.
"""
from dataclasses import asdict
from datetime import date
from math import isfinite
from .chronological_manager_replay import run
from .manager_evolution_v1 import population, offspring, identity


def metrics(result):
    values=[100000.]+[float(row[1]) for row in result['nav']]
    if len(values)<3 or any(not isfinite(v) or v<=0 for v in values):
        raise ValueError('finite positive NAV for at least two sessions required')
    peak=values[0]
    drawdown=0.
    for value in values:
        peak=max(peak,value)
        drawdown=max(drawdown,1-value/peak)
    return (values[-1]/values[0]-1.,-drawdown)


def evolve(factory, *, train_start, train_end, validation_end,
           size=2, generations=1, seed=7, min_samples=5):
    """Factory(end_date) -> (days, replay_options).

    Training starts with $100k. Validation replays the prefix to retain causal
    calibration/positions, but scores only the later interval. The validation
    period cannot choose a genome. No proof set is read by this function.
    """
    if not 2<=size<=16 or not 1<=generations<=5:
        raise ValueError('bounded to 2..16 genomes and 1..5 generations')
    bounds=[date.fromisoformat(d) for d in (train_start,train_end,validation_end)]
    if not bounds[0]<bounds[1]<bounds[2]:raise ValueError('strict chronological windows required')

    def evaluate(genome,end):
        days,options=factory(end)
        days=list(days)
        dates=[row[0] for row in days]
        if len(days)>252:raise ValueError('first-year pilot bounded to 252 sessions')
        if len(days)<2 or dates[0]!=train_start or dates[-1]!=end:
            raise ValueError('factory must return exact requested date window')
        if any(d<train_start or d>end for d in dates):raise ValueError('future day in replay')
        forbidden={'genes','min_samples'} & set(options)
        if forbidden:raise ValueError('factory cannot override manager policy')
        return run(days,genes=genome,min_samples=min_samples,**options)

    genomes=population(size,seed)
    history=[]
    scored=[]
    training_results={}
    for generation in range(generations):
        scored=[]
        records=[]
        for genome in genomes:
            result=evaluate(genome,train_end)
            fitness=metrics(result)
            training_results[identity(genome)]=result
            scored.append((genome,fitness))
            records.append({'identity':identity(genome),'fitness':fitness,
                            'fills':len(result['ledger'])})
        history.append(records)
        if generation+1<generations:
            genomes=offspring(scored,n=size,seed=seed+generation+1)
    # Predeclared scalar tie break: net growth, then smaller drawdown, then ID.
    winner,fitness=max(scored,key=lambda x:(x[1][0],x[1][1],identity(x[0])))
    validation=evaluate(winner,validation_end)
    trained=training_results[identity(winner)]
    if ([r for r in validation['nav'] if r[0]<=train_end]!=trained['nav'] or
        [r for r in validation['ledger'] if r[0]<=train_end]!=trained['ledger'] or
        [r for r in validation['decisions'] if r['date']<=train_end]!=trained['decisions']):
        raise ValueError('validation changed training prefix: noncausal or nondeterministic factory')
    baseline=[row for row in validation['nav'] if row[0]<=train_end][-1][1]
    later=[row for row in validation['nav'] if row[0]>train_end]
    if not later:raise ValueError('missing validation sessions')
    scaled={'nav':[(r[0],r[1]/baseline*100000.) for r in later]}
    # Include boundary NAV so a first-validation-day loss counts in drawdown.
    validation_fitness=metrics({'nav':[(train_end,100000.)]+scaled['nav']})
    return {'status':'RESEARCH_CHRONOLOGICAL_MANAGER_EVOLUTION',
            'windows':{'train':[train_start,train_end],
                       'validation_after':train_end,'validation_end':validation_end},
            'selected':{'identity':identity(winner),'genes':asdict(winner),
                        'training_fitness':fitness},
            'history':history,'validation_fitness':validation_fitness,
            'validation_fills':sum(f[0]>train_end for f in validation['ledger']),
            'differentiated_training_fitness':len({v for _,v in scored})>1,
            'readiness':'UNCERTIFIED: native sources, feature parity and execution parity required'}
