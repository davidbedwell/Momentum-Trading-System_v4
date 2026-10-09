"""DEV80 conditional exit v2: causal lagged price-path signals, paired benchmarks.
Feasibility experiment only. No blind bank access or scientific certification.
"""
import argparse,json,pathlib
import numpy as np,pandas as pd
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
R=pathlib.Path('Research/Runs/gen1-merit-screen-20261008');P=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
H=(1,2,3,5,7,10,15,20,63)
def simulate(ret,cost,g):
    """Outcome at open k only triggers a possible exit at open k+1."""
    n,h=ret.shape;valid=np.isfinite(ret)&np.isfinite(cost)
    prefix=np.logical_and.accumulate(valid,axis=1);last=prefix.sum(axis=1)-1
    if np.any(last<1):raise ValueError('requires two executable exit opens')
    prev=np.concatenate((np.zeros((n,1)),ret[:,:-1]),axis=1)
    peak=np.maximum.accumulate(np.where(np.isfinite(prev),prev,-np.inf),axis=1)
    draw=peak-prev
    # Conditional disjunction of stop-loss, trailing reversal, profit capture;
    # only previously observed executable-open state can trigger a later fill.
    age,stop,trail,take,mode=g
    exit_signal=(prev<=stop)|((draw>=trail)&(prev>0))
    if int(mode)==1:exit_signal|=(prev>=take)
    if int(mode)==2:exit_signal|=(prev>=take)&(draw>=trail/2)
    exit_signal[:,:max(1,int(age))]=False
    exit_signal &=prefix
    exit_signal[np.arange(n),last]=True
    idx=np.argmax(exit_signal,axis=1)
    return ret[np.arange(n),idx]-cost[np.arange(n),idx],idx,last

def score(x):return float(np.mean(x)+0.4*min(0.,float(np.quantile(x,.05))))
def run(limit,popsize,gens,maxevents):
    out=R/'exit_ga_conditional_v2_20261009';out.mkdir(exist_ok=True)
    rng=np.random.default_rng(20261009);f=pd.read_parquet(P/'dev80_predictors.parquet');d=pd.to_datetime(f.effective_date)
    raw=pd.read_parquet(P/'dev80_raw.parquet');assert len(f)==len(raw) and np.array_equal(f.security_id.to_numpy(),raw.security_id.to_numpy()) and np.array_equal(pd.to_datetime(f.effective_date).to_numpy(),pd.to_datetime(raw.date).to_numpy())
    a=np.load(R/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz');e=a['endpoint_return'][:,:63];compiler=CausalSignalCompiler(f)
    gs=[json.loads(s) for s in (R/'all_candidates.jsonl').open()];chosen=np.linspace(0,len(gs)-1,min(limit,len(gs)),dtype=int)
    results=[]
    for ci in chosen:
        g=gs[int(ci)];side=1 if g['side']=='LONG' else -1
        entry=np.logical_and.reduce([compiler.compile(fam,gene) for fam,gene in g['chromosomes']]);c=a['long_roundtrip'] if side==1 else a['short_roundtrip'];c=c[:,:63] if c.ndim==2 else np.broadcast_to(c[:,None],e.shape)
        prefix=np.logical_and.accumulate(np.isfinite(e)&np.isfinite(c),axis=1).sum(axis=1);ok=prefix>=2
        train=np.flatnonzero(entry&(d<'2016-01-01').to_numpy()&ok);test=np.flatnonzero(entry&(d>='2021-01-01').to_numpy()&ok)
        if len(train)>maxevents:train=train[np.linspace(0,len(train)-1,maxevents,dtype=int)]
        if len(test)>maxevents:test=test[np.linspace(0,len(test)-1,maxevents,dtype=int)]
        if len(train)<40 or len(test)<20:
            rec={'index':g['index'],'side':g['side'],'status':'INSUFFICIENT_ENTRY_SUPPORT','train':len(train),'test':len(test)}
        else:
            tr=side*e[train];te=side*e[test];tc=c[train];ec=c[test]
            # Benchmarks are evaluated on the SAME sample of events, censoring at
            # each event's last consecutive executable exit. No path gap imputation.
            def benchmarks(r,k):
                valid=np.logical_and.accumulate(np.isfinite(r)&np.isfinite(k),axis=1);last=valid.sum(axis=1)-1
                return {str(h):r[np.arange(len(r)),np.minimum(h-1,last)]-k[np.arange(len(r)),np.minimum(h-1,last)] for h in H}
            btrain=benchmarks(tr,tc);btest=benchmarks(te,ec)
            # Benchmark floor fixed from training only, not selected on test.
            baseline=max(H,key=lambda h:score(btrain[str(h)]))
            def random_gene():return np.array([rng.integers(1,42),rng.uniform(-.18,-.005),rng.uniform(.005,.3),rng.uniform(.01,.3),rng.integers(0,3)],float)
            pop=np.stack([random_gene() for _ in range(popsize)])
            def fitness(z):
                rr,_,_=simulate(tr,tc,z)
                return score(rr)-score(btrain[str(baseline)])-0.0002*(z[4]>0)
            for _ in range(gens):
                fit=np.array([fitness(z) for z in pop]);elite=pop[np.argsort(fit)[-max(2,popsize//4):]]
                offspring=elite[rng.integers(len(elite),size=popsize-len(elite))]+rng.normal(0,[3,.02,.025,.025,.5],(popsize-len(elite),5))
                pop=np.vstack((elite,offspring));pop[:,0]=np.clip(np.rint(pop[:,0]),1,62);pop[:,1]=np.clip(pop[:,1],-.3,-.001);pop[:,2:4]=np.clip(pop[:,2:4],.002,.5);pop[:,4]=np.clip(np.rint(pop[:,4]),0,2)
            best=pop[np.argmax([fitness(z) for z in pop])];realized,ix,last=simulate(te,ec,best)
            paired={str(h):{'benchmark_mean':float(np.mean(btest[str(h)])),'gain_mean':float(np.mean(realized-btest[str(h)])),'paired_n':len(test)} for h in H}
            rec={'index':g['index'],'side':g['side'],'status':'UNCERTIFIED_CHRONOLOGICAL_V2','train':len(train),'test':len(test),'policy':best.tolist(),'train_baseline_horizon':baseline,'test_ga_mean':float(realized.mean()),'test_gain_vs_frozen_train_baseline':paired[str(baseline)]['gain_mean'],'test_exit_age_mean':float(np.mean(ix+1)),'test_censored_fraction':float(np.mean(last<62)),'paired_horizon_benchmarks':paired}
        results.append(rec);print(json.dumps(rec),flush=True);(out/'checkpoint.json').write_text(json.dumps({'done':len(results),'requested':len(chosen),'results':results},indent=2))
    (out/'report.json').write_text(json.dumps({'status':'UNCERTIFIED_DEV80_CONDITIONAL_V2','results':results,'limitations':['Open-to-open returns lagged one session; full close-T decision feature panel not yet implemented','End-of-series paths censored; forced liquidation at last available open is an analytical convention, not a live trade signal','No delisting price recovery or market-episode independence','No portfolio overlap constraints or borrow availability','Not certified; do not promote or access protected banks']},indent=2));print('V2_FINISHED',len(results),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=12);p.add_argument('--individuals',type=int,default=32);p.add_argument('--generations',type=int,default=12);p.add_argument('--max-events',type=int,default=400);x=p.parse_args();run(x.limit,x.individuals,x.generations,x.max_events)
