"""Bounded GA9-A chronological synthetic proof (two generations, six genomes)."""
import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import random
import time
import numpy as np
from .opportunity import Strategy, load_synthetic, fit, allocate, opportunity, strategy_outcomes

DEFAULT_ROOT=Path('/opt/mts/synthetic-market-lab/runs/causal_native_features')


def market(p,a,b):
    # Synthetic broad-market proxy: fixed equal-weight sleeves, same initial costs,
    # cash on first decision day. This is not SPY or a real market claim.
    nav=np.r_[100000.,100000*np.mean(p.close[a+1:b]/(p.open[a+1]*1.00060005),axis=1)]
    return dict(cagr=float((nav[-1]/100000)**(252/(b-a))-1),final_nav=float(nav[-1]))


def run(output, root=DEFAULT_ROOT):
    start=time.monotonic(); out=Path(output)
    out.mkdir(parents=True,exist_ok=False)
    prices=Path(root)/'universe_1_eight_family.parquet'; membership=Path(root)/'universe_1_ga4_native.parquet'
    p=load_synthetic(prices,membership)
    if p.close.shape != (1260,500): raise ValueError('Proof expects one 500-stock, 1260-session scenario')
    rng=random.Random(9009)
    def child(parents):
        a,b=rng.sample(parents,2)
        fields={k:rng.choice([asdict(a)[k],asdict(b)[k]]) for k in asdict(a)}
        choices=dict(family=['momentum','trend','relative_strength','recursive','volatility'],horizon=[5,20,60],
                     threshold=[-.2,0.,.5],add=[.005,.01,.02],reduce=[-.005,-.01,-.015],trailing=[.03,.05,.08])
        for key,values in choices.items():
            if rng.random()<.4: fields[key]=rng.choice(values)
        return Strategy(**fields)
    population=[Strategy(family=f,horizon=h) for f,h in [('momentum',5),('trend',20),('relative_strength',60),('recursive',20),('volatility',5),('momentum',60)]]
    journal=[]; cache={}; validation_market=market(p,756,1008)
    for generation in range(2):
        ranked=[]
        for s in population:
            key=json.dumps(asdict(s),sort_keys=True)
            if key not in cache:
                model=fit(p,s); result=allocate(p,model,756,1008,False); q=result['metrics']
                excess=q['cagr']-validation_market['cagr']
                # Hard observed risk gate, then distance from portfolio ambition.
                fitness=(q['max_drawdown']<.08,excess-.20,-q['max_drawdown'])
                cache[key]=(fitness,model,q)
            fitness,model,q=cache[key]; ranked.append((fitness,key,s))
            journal.append(dict(generation=generation+1,strategy=asdict(s),fitness=fitness,metrics=q))
        ranked.sort(key=lambda x:(x[0],x[1]),reverse=True)
        elites=[x[2] for x in ranked[:3]]
        population=elites[:2]+[child(elites) for _ in range(4)]
    # Across both generations, freeze winner before external forward evaluation.
    winner=max(cache,key=lambda key:(cache[key][0],key)); _,model,validation=cache[winner]
    (out/'frozen_model.json').write_text(json.dumps(model,indent=2))
    result=allocate(p,model,1008,1260); reference=market(p,1008,1260)
    for event, ledger in zip(result['events'],result['equity']):
        ordered={x['ticker'] for x in event['order_details']}
        event['hold_details']=[dict(action='HOLD',ticker=x['ticker'],reason='no_stock_or_allocator_exit_reduce_add_trigger')
                               for x in ledger['holdings_detail'] if x['ticker'] not in ordered]
    for filename,data in [('daily_ledger.jsonl',result['equity']),('decisions.jsonl',result['events']),('fills.jsonl',result['fills'])]:
        with (out/filename).open('w') as f:
            for row in data:f.write(json.dumps(row,allow_nan=False)+'\n')
    # Incumbents remain forecastable after leaving the discovery pool.
    with (out/'opportunities.jsonl').open('w') as f:
        for t,row in zip(range(1008,1260),result['equity']):
            incumbents={p.symbols.index(x['ticker']) for x in row['holdings_detail']}
            for j in sorted(set(np.flatnonzero(p.screen_mask[t]))|incumbents):
                f.write(json.dumps(opportunity(p,model,t,j),allow_nan=False)+'\n')
    s=Strategy(**model['strategy']); y,down=strategy_outcomes(p,s,1260)
    buckets={}
    for t in range(1008,1260-s.horizon-1):
        for j in np.flatnonzero(p.screen_mask[t]):
            r=opportunity(p,model,t,j)
            if r['entry_eligible'] and np.isfinite(y[t,j]):
                b=int(np.digitize(p.features[s.family][t,j],[-1,0,.5,1,2]))
                buckets.setdefault(b,[]).append((r['expected_net_return'],y[t,j],r['downside_p10'],down[t,j],r['probability_positive']))
    calibration=[]
    for b,rows in buckets.items():
        a=np.array(rows);calibration.append(dict(bin=b,n=len(a),predicted_mean=float(a[:,0].mean()),realized_mean=float(a[:,1].mean()),
            bias=float((a[:,0]-a[:,1]).mean()),downside_p10_coverage=float(np.mean(a[:,3]>=a[:,2])),
            predicted_probability_positive=float(a[:,4].mean()),observed_positive=float(np.mean(a[:,1]>0)),brier=float(np.mean((a[:,4]-(a[:,1]>0))**2))))
    # Verify execution chronology, NAV identity and pool eligibility on actual artifacts.
    date_to_i={str(d.date()):i for i,d in enumerate(p.dates)}
    for fill in result['fills']:
        ti=date_to_i[fill['date']];di=date_to_i[fill['decision_date']]
        assert ti==di+1
        j=p.symbols.index(fill['ticker']);assert fill['raw_open']==p.open[ti,j]
        if fill['action']=='ENTRY': assert p.screen_mask[di,j] and p.eligible[di,j] and p.eligible[ti,j]
    assert all(abs(r['nav']-r['cash']-r['unsettled']-r['holdings'])<1e-5 for r in result['equity'])
    assert np.all(p.screen_mask.sum(axis=1)<=150) and not (p.screen_mask & ~p.eligible).any()
    q=result['metrics'];excess=q['cagr']-reference['cagr']
    report=dict(label='SYNTHETIC_ENGINEERING_ONLY',stocks=500,sessions=1260,scenario=1,
        source_prices=str(prices),source_membership=str(membership),
        source_sha256={x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in [prices,membership]},
        split=dict(train=[0,504],calibration=[504,756],selection=[756,1008],external_forward=[1008,1260]),
        generations=2,population=6,unique_evaluations=len(cache),journal=journal,winner=model,validation=validation,
        forward=q,market_proxy=reference,excess_cagr_percentage_points=100*excess,
        target=dict(excess_cagr_percentage_points=20,max_drawdown=.08,met=bool(excess>=.20 and q['max_drawdown']<.08)),
        calibration=calibration,actions=dict(Counter(x['action'] for x in result['fills'])),
        decision_actions=dict(Counter(x['action'] for e in result['events'] for x in e['order_details'])),
        no_trade_days=sum(e['decision']=='NO_TRADE' for e in result['events']),holds=result['audit']['holds'],
        audit=result['audit'],pool_max=int(p.screen_mask.sum(axis=1).max()),runtime_seconds=time.monotonic()-start,
        checks=['next_session_open','raw_open_match','entry_PIT_pool','NAV_identity','pool_cap_and_eligibility'])
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    print(json.dumps({k:report[k] for k in ['forward','market_proxy','excess_cagr_percentage_points','target','actions','holds','runtime_seconds']},indent=2))
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--root',type=Path,default=DEFAULT_ROOT)
    a=ap.parse_args();run(a.output,a.root)
