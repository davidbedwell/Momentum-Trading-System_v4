"""Bounded, resumable manager-only GA on explicitly synthetic prices."""
import argparse, hashlib, json, random, time
from dataclasses import asdict, replace
from pathlib import Path
import numpy as np
import pandas as pd
from .execution import Panel, Gene, Manager, FAMILIES, replay


def fixture():
    rng=np.random.default_rng(91029); n=1260; k=6
    t=np.arange(n); regimes=np.sin(t/85)
    ret=.00022+.0018*np.sin(t[:,None]/37+np.arange(k))+rng.normal(0,.006,(n,k))
    ret[756:]+=-.00015  # predeclared holdout distribution shift
    close=100*np.cumprod(1+ret,axis=0); opens=np.vstack([close[0],close[:-1]])
    frame=pd.DataFrame(close); mom=(frame/frame.shift(12)-1).fillna(0).to_numpy()*20
    trend=(frame/frame.rolling(35,min_periods=1).mean()-1).to_numpy()*25
    features={f:mom.copy() for f in FAMILIES}; features['trend']=trend
    features['relative_strength']=pd.DataFrame(mom).rank(axis=1,pct=True).to_numpy()*2-1
    niche=np.tile(np.arange(k)%3,(n,1))
    p=Panel(pd.bdate_range('2030-01-01',periods=n),[f'SYN_{i}' for i in range(k)],opens,close,np.zeros_like(close),ret,features,niche,regimes,
            sectors=tuple(str(i%3) for i in range(k)),eligible=np.ones((n,k),bool),screen_mask=np.ones((n,k),bool),screen_score=mom)
    genes=[Gene(f,niche=i,threshold=.05,weight=.075,hold_sessions=35,add=.008,reduce=-.008) for i in range(3) for f in ('momentum','relative_strength')]
    return p,genes


def ident(m): return hashlib.sha256(json.dumps(asdict(m),sort_keys=True).encode()).hexdigest()[:16]

def mutate(m,r):
    choices=dict(slots=[0,2,4,6],reserve=[.1,.3,.6,1.],risk_cap=[.004,.008,.014],sector_cap=[.1,.2,.3],correlation=[.6,.85,.99],replacement=[.1,.4,1.],entry_floor=[-.2,.1,.4,.8],size_scale=[.3,.6,1.,1.3],score_size=[0.,.3,.8],allow_add=[False,True],reduce_floor=[-1e30,-.1,.1],exit_floor=[-1e30,-.3,0.])
    d=asdict(m)
    for key,values in choices.items():
        if r.random()<.3: d[key]=r.choice(values)
    d['niche_bias']=tuple(r.uniform(-.4,.4) if r.random()<.3 else x for x in m.niche_bias)
    d['specialist_bias']=tuple(r.uniform(-.5,.5) if r.random()<.3 else x for x in (m.specialist_bias or (0.,)*6))
    return Manager(**d)


def evaluate(p,g,m,a,b,detail=False):
    result=replay(p,g,m,p.dates[a],p.dates[b-1]+pd.Timedelta(days=1),detail=detail,edge_mode=True,niche_first=True)
    # Synthetic equal-weight buy and hold; first executable open, same entry cost.
    bench=np.r_[100000.,np.mean(p.close[a+1:b]/p.open[a+1],axis=1)*100000/1.00060005]
    bcagr=float((bench[-1]/100000)**(252/(b-a))-1)
    q=result['metrics']; score=q['cagr']-bcagr-2*q['max_drawdown']-q['costs']/100000-.1*q['mean_concentration_hhi']
    if not q['feasible']: score-=10+100*max(0,q['max_drawdown']-.08)
    q.update(benchmark_cagr=bcagr,benchmark_final_nav=float(bench[-1]),excess_cagr=q['cagr']-bcagr,fitness=score)
    if detail:
        for row,bv in zip(result['equity'],bench): row['benchmark_nav']=float(bv)
    return result


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True); p,g=fixture();r=random.Random(91029); start=time.monotonic(); prior=0.
    base=Manager(slots=6,reserve=.1,specialist_bias=(0.,)*6)
    statepath=out/'checkpoint.json'; history=[]; cache={}; begin=0
    pop=[base,replace(base,slots=0)]; pop += [mutate(base,r) for _ in range(98)]
    if statepath.exists():
        state=json.loads(statepath.read_text());begin=state['next_generation'];pop=[Manager(**x) for x in state['population']];history=state['history'];cache=state['cache'];prior=state['runtime_seconds']
        def tup(x): return tuple(tup(v) if isinstance(v,list) else v for v in x)
        r.setstate(tup(state['rng']))
    if not (out/'fixture.npz').exists():
        np.savez_compressed(out/'fixture.npz',dates=p.dates.to_numpy(),symbols=p.symbols,open=p.open,close=p.close,returns=p.returns,niche=p.niche,**p.features)
    baseline=evaluate(p,g,base,0,756,True); (out/'baseline_train.json').write_text(json.dumps(baseline))
    for gen in range(begin,25):
        ranked=[]; rows=[]
        for m in pop:
            key=ident(m)
            if key not in cache:
                z=evaluate(p,g,m,0,756,True)
                signature=hashlib.sha256(json.dumps([(f['date'],f['ticker'],f['gene'],f['action'],round(f['notional'],4)) for f in z['fills']]).encode()).hexdigest()
                cache[key]=dict(metrics=z['metrics'],signature=signature)
            c=cache[key];ranked.append((c['metrics']['fitness'],key,m));rows.append(dict(id=key,**c))
        ranked.sort(key=lambda x:x[0],reverse=True)
        scores=[x[0] for x in ranked]; best=ranked[0]
        row=dict(generation=gen+1,best=scores[0],median=float(np.median(scores)),unique_genomes=len(set(x[1] for x in ranked)),unique_decisions=len(set(x['signature'] for x in rows)),feasible=sum(x['metrics']['feasible'] for x in rows),best_id=best[1],best_metrics=cache[best[1]]['metrics'],runtime_seconds=prior+time.monotonic()-start)
        history.append(row);(out/f'generation_{gen+1:02}.json').write_text(json.dumps(dict(summary=row,candidates=rows,population=[asdict(m) for m in pop])))
        print(json.dumps(row),flush=True)
        elites=[x[2] for x in ranked[:10]];pop=[x[2] for x in ranked[:5]]
        while len(pop)<100:
            # Uniform crossover plus mutation; selection uses training only.
            a,b=r.sample(elites,2);d={k:r.choice([asdict(a)[k],asdict(b)[k]]) for k in asdict(a)};pop.append(mutate(Manager(**d),r))
        state=dict(next_generation=gen+1,population=[asdict(m) for m in pop],history=history,cache=cache,rng=r.getstate(),runtime_seconds=prior+time.monotonic()-start)
        tmp=out/'checkpoint.tmp';tmp.write_text(json.dumps(state));tmp.replace(statepath)
        if time.monotonic()-start>1800: return
    # Freeze winner before touching holdout.
    winner=next(m for m in pop if ident(m)==history[-1]['best_id'])
    artifacts=dict(winner_train=evaluate(p,g,winner,0,756,True),winner_holdout=evaluate(p,g,winner,756,1260,True),baseline_holdout=evaluate(p,g,base,756,1260,True))
    for name,value in artifacts.items(): (out/f'{name}.json').write_text(json.dumps(value))
    report=dict(label='SYNTHETIC_ENGINEERING_ONLY',population=100,generations=25,workers=1,sessions=1260,stocks=6,train_sessions=756,holdout_sessions=504,cash_policy='uninvested cash, zero yield; no SGOV return assumed',winner=asdict(winner),history=history,unique_evaluations=len(cache),baseline_train=baseline['metrics'],**{k:v['metrics'] for k,v in artifacts.items()},runtime_seconds=prior+time.monotonic()-start,stop_reason='generation_cap')
    (out/'report.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);run(ap.parse_args().output)
