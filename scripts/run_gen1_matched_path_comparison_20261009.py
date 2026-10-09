"""Matched distressed winner/loser path study, DEV80. Descriptive pilot, not certification."""
import argparse,json,time,pathlib
import numpy as np,pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
STORE=ROOT/'shared_path_store_20261009'
def run(limit,neighbors):
    start=time.time();out=ROOT/'matched_winner_loser_20261009';out.mkdir(exist_ok=True)
    f=pd.read_parquet('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
    assert len(f)==len(pd.read_parquet(STORE/'decision_features.parquet'))
    dates=pd.to_datetime(f.effective_date)
    train=(dates<'2016-01-01') ;test=(dates>='2021-01-01')
    compiler=CausalSignalCompiler(f)
    candidates=[json.loads(s) for s in open(ROOT/'all_candidates.jsonl')]
    results=[]
    # Same-genome matched histories; a matched neighbor must predate the held-out test.
    for r in candidates[:limit]:
        mask=np.logical_and.reduce([compiler.compile(family,gene) for family,gene in r['chromosomes']])
        side=1 if r['side']=='LONG' else -1
        for checkpoint in (5,10,15):
            a=pd.read_parquet(STORE/f'checkpoint_{checkpoint:02d}.parquet')
            cp=a.checkpoint_gross_return.to_numpy()
            future=a.continuation_gross_return.to_numpy()
            costs20=a.long_exit_cost_at_20.to_numpy() if side==1 else a.short_exit_cost_at_20.to_numpy()
            costsnow=a.long_exit_cost_at_checkpoint.to_numpy() if side==1 else a.short_exit_cost_at_checkpoint.to_numpy()
            # Forward outcome label: net result at frozen 20-session terminal horizon.
            # Checkpoint entry-to-date net return and past-only context are features.
            end_net=side*(cp+future)-costs20
            features=np.column_stack([side*cp,
                f['return_5__v1'].to_numpy(float)*side,
                f['return_20__v1'].to_numpy(float)*side,
                f['close_to_sma_50__v1'].to_numpy(float),
                f['close_to_sma_200__v1'].to_numpy(float),
                f['breadth_above_sma_200__v1'].to_numpy(float),
                np.full(len(f),checkpoint,dtype=float)])
            valid=mask&np.isfinite(features).all(axis=1)&np.isfinite(end_net)&np.isfinite(costsnow)
            # Restrict to states under water at the checkpoint; winner means positive
            # net terminal return, not knowledge available at decision time.
            distressed=valid&(side*cp-costsnow<0)
            trainids=np.flatnonzero(distressed&train)
            testids=np.flatnonzero(distressed&test)
            rec={'index':r['index'],'side':r['side'],'checkpoint':checkpoint,
                'historical_distressed':len(trainids),'heldout_distressed':len(testids)}
            winners=trainids[end_net[trainids]>0];losers=trainids[end_net[trainids]<=0]
            rec['historical_recovered']=len(winners);rec['historical_failed']=len(losers)
            if min(len(winners),len(losers))<neighbors or len(testids)<20:
                rec['status']='INSUFFICIENT_MATCH_SUPPORT';results.append(rec);continue
            scaler=StandardScaler().fit(features[trainids])
            trainx=scaler.transform(features[trainids]);testx=scaler.transform(features[testids])
            nn=NearestNeighbors(n_neighbors=neighbors,algorithm='auto').fit(trainx)
            distances,near=nn.kneighbors(testx)
            nearids=trainids[near]
            frac=np.mean(end_net[nearids]<=0,axis=1)
            observed=(end_net[testids]<=0)
            # No learned exit decision here; diagnostic classification only.
            rec.update(status='MATCHED_DIAGNOSTIC_UNCERTIFIED',
                historical_failure_rate=float(np.mean(end_net[trainids]<=0)),
                heldout_failure_rate=float(np.mean(observed)),
                mean_neighbor_failure_probability=float(np.mean(frac)),
                mean_match_distance=float(np.mean(distances)),
                ambiguous_fraction=float(np.mean((frac>=.3)&(frac<=.7))),
                high_failure_signal_fraction=float(np.mean(frac>=.7)),
                high_failure_signal_false_exit_fraction=float(np.mean((frac>=.7)&(~observed))),
                high_failure_signal_precision=float(np.mean(observed[frac>=.7])) if np.any(frac>=.7) else None,
                high_failure_signal_recall=float(np.mean((frac>=.7)[observed])) if np.any(observed) else None)
            results.append(rec)
        with open(out/'results.jsonl','w') as dest:
            for row in results:dest.write(json.dumps(row,allow_nan=False)+'\n')
        (out/'progress.json').write_text(json.dumps({'genomes_done':len({r['index'] for r in results}),'genomes_requested':limit,'seconds':round(time.time()-start,1)}))
    manifest={'status':'MATCHED_WINNER_LOSER_PILOT_UNCERTIFIED','scope':'DEV80 only',
        'genomes_evaluated':limit,'checkpoints':[5,10,15],'neighbors':neighbors,
        'train_before':'2016-01-01','heldout_after':'2021-01-01',
        'limitations':['Only 20-session terminal labels','No sector-at-checkpoint dynamics; context observed at entry only','No portfolio replay or parent promotion','Overlapping market episodes require cluster-aware validation','Fixed .7 reporting threshold descriptive, not a trading trigger'],
        'protected_banks_touched':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=12);p.add_argument('--neighbors',type=int,default=25);args=p.parse_args();run(args.limit,args.neighbors)
