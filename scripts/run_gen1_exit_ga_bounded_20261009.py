"""DEV80-only bounded evolutionary sequential-exit feasibility experiment.

A pilot, NOT a certified strategy: one trade per entry signal, overlapping trades
and common market episodes; no portfolio sizing, borrow availability or PIT audit.
"""
import argparse,json,pathlib,time
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
F=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
OUT=R/'exit_ga_bounded_pilot_20261009'
def evaluate(returns,cost,genes):
    # Each gene: threshold for signed unrealized return, age, and optional trailing drawdown.
    threshold,earliest,trail=genes
    n,h=returns.shape
    peak=np.maximum.accumulate(returns,axis=1)
    valid=np.isfinite(returns)&np.isfinite(cost)
    exits=(returns<=threshold)|((peak-returns)>=trail)
    exits[:, :max(0,int(earliest)-1)]=False
    exits &= valid
    # An exit at session t uses only data through prior close: outcome at next open.
    # Here returns[:,t] is already the next-open executable return, hence using it
    # as an exit trigger would leak. Shift signals by one full session.
    signals=np.zeros_like(exits)
    signals[:,1:]=exits[:,:-1]
    signals[:,-1]=True
    ix=np.argmax(signals,axis=1)
    realized=returns[np.arange(n),ix]-cost[np.arange(n),ix]
    horizon=returns[:,-1]-cost[:,-1]
    ok=np.isfinite(realized)&np.isfinite(horizon)
    return realized[ok],horizon[ok],ix[ok]
def run(limit,individuals,generations,max_events):
    OUT.mkdir(exist_ok=True)
    rng=np.random.default_rng(20261009)
    f=pd.read_parquet(F);d=pd.to_datetime(f.effective_date)
    a=np.load(R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz')
    e=a['endpoint_return'][:,:63]
    compiler=CausalSignalCompiler(f)
    candidates=[json.loads(x) for x in (R/'all_candidates.jsonl').open()]
    # Preserve all 4,360 in the candidate population. Budgeted pilot samples a
    # deterministic spread; this does not select winners by unseen outcomes.
    chosen=np.linspace(0,len(candidates)-1,min(limit,len(candidates)),dtype=int)
    results=[]
    for ci in chosen:
        g=candidates[int(ci)];side=1 if g['side']=='LONG' else -1
        entry=np.logical_and.reduce([compiler.compile(fam,gene) for fam,gene in g['chromosomes']])
        costs=a['long_roundtrip'] if side==1 else a['short_roundtrip']
        if costs.ndim==1:costs=np.broadcast_to(costs[:,None],e.shape)
        costs=costs[:,:63]
        train=np.flatnonzero(entry&(d<'2016-01-01').to_numpy()&np.isfinite(e[:,62])&np.isfinite(costs[:,62]))
        test=np.flatnonzero(entry&(d>='2021-01-01').to_numpy()&np.isfinite(e[:,62])&np.isfinite(costs[:,62]))
        train=train[:max_events];test=test[:max_events]
        if len(train)<40 or len(test)<20:
            results.append({'index':g['index'],'status':'INSUFFICIENT_COMPLETE_PATHS','train':len(train),'test':len(test)});continue
        tr=side*e[train];te=side*e[test];tc=costs[train];ec=costs[test]
        pop=np.column_stack([rng.uniform(-.2,.04,individuals),rng.integers(1,61,individuals),rng.uniform(.005,.3,individuals)])
        def score(z):
            r,h,_=evaluate(tr,tc,z)
            return -1e6 if len(r)!=len(tr) else float(np.mean(r)-.4*np.quantile(r,.05)*(-1 if np.quantile(r,.05)<0 else 0))
        for generation in range(generations):
            fitness=np.array([score(z) for z in pop]);elite=pop[np.argsort(fitness)[-max(2,individuals//4):]]
            pop=np.vstack([elite,elite[rng.integers(len(elite),size=individuals-len(elite))]+rng.normal(0,[.015,3,.025],(individuals-len(elite),3))])
            pop[:,0]=np.clip(pop[:,0],-.3,.1);pop[:,1]=np.clip(np.rint(pop[:,1]),1,62);pop[:,2]=np.clip(pop[:,2],.002,.5)
        fitness=np.array([score(z) for z in pop]);best=pop[np.argmax(fitness)]
        realized,horizon,ix=evaluate(te,ec,best)
        rec={'index':g['index'],'status':'UNSEEN_CHRONOLOGICAL_PILOT_UNCERTIFIED','side':g['side'],'train_events':len(train),'test_events':len(test),'policy':best.tolist(),'train_objective':float(fitness.max()),'test_mean_net':float(realized.mean()),'test_horizon_mean_net':float(horizon.mean()),'test_gain_vs_63':float(np.mean(realized-horizon)),'test_exit_before_63':float(np.mean(ix<62))}
        results.append(rec);print(json.dumps(rec),flush=True)
        (OUT/'checkpoint.json').write_text(json.dumps({'done':len(results),'requested':len(chosen),'results':results},indent=2))
    report={'status':'BOUNDED_EXIT_GA_PILOT_UNCERTIFIED','scope':'DEV80_ONLY','requested_genomes':len(chosen),'original_population':len(candidates),'results':results,'limitations':['PIT feature release timing not independently certified','Exit trigger uses prior executable-open return proxy, not intraday close features','Training and test entries overlap and market episodes are not independent','No portfolio constraints or independent episode inference','No DEV37 DEV50 or BLIND17 touched','Threshold search is pilot evolutionary search, not full conditional-matrix GA']}
    (OUT/'report.json').write_text(json.dumps(report,indent=2));print('PILOT_FINISHED',len(results),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=6);p.add_argument('--individuals',type=int,default=24);p.add_argument('--generations',type=int,default=8);p.add_argument('--max-events',type=int,default=400)
    z=p.parse_args();run(z.limit,z.individuals,z.generations,z.max_events)
