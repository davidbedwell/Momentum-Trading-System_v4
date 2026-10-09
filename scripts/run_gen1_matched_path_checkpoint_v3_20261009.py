"""Matched distressed winner/loser path study, DEV80. Descriptive pilot, not certification."""
import argparse,json,time,pathlib
import numpy as np,pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
STORE=ROOT/'shared_path_store_20261009'
def run(limit,neighbors):
    start=time.time();out=ROOT/'matched_winner_loser_checkpoint_v3_20261009';out.mkdir(exist_ok=True)
    f=pd.read_parquet('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet')
    assert len(f)==len(pd.read_parquet(STORE/'decision_features.parquet'))
    dates=pd.to_datetime(f.effective_date)
    train=(dates<'2016-01-01');calibrate=(dates>='2016-07-15')&(dates<'2020-06-01');test=(dates>='2021-01-01')
    compiler=CausalSignalCompiler(f)
    # PIT checkpoint context: day T+c close is observable at T+1+c open.
    # Join by market-session calendar, NOT by sparse per-security row offsets.
    calendar=pd.Index(sorted(dates.unique()))
    date_to_pos=pd.Series(np.arange(len(calendar)),index=calendar)
    positions=dates.map(date_to_pos).to_numpy(dtype=int)
    lookup=pd.MultiIndex.from_frame(f[['security_id','effective_date']].assign(effective_date=dates))
    if not lookup.is_unique: raise AssertionError('Nonunique PIT security/date')
    feature_cols=['return_5__v1','return_20__v1','close_to_sma_50__v1','close_to_sma_200__v1','breadth_above_sma_200__v1']
    checkpoint_context={}
    for c in (5,10,15):
        shifted=np.minimum(positions+c,len(calendar)-1)
        future_dates=calendar.take(shifted)
        keys=pd.MultiIndex.from_arrays([f.security_id.to_numpy(),future_dates])
        valid_date=(positions+c)<len(calendar)
        aligned=f[feature_cols].reindex(index=np.arange(len(f)))
        by_key=f.set_index(lookup)[feature_cols]
        vals=by_key.reindex(keys).to_numpy(dtype=float).copy()
        vals[~valid_date,:]=np.nan
        checkpoint_context[c]=vals
    candidates=[json.loads(s) for s in open(ROOT/'all_candidates.jsonl')]
    results=[]; predictions=[]
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
            features=np.column_stack([side*cp, checkpoint_context[checkpoint][:,0]*side, checkpoint_context[checkpoint][:,1]*side,checkpoint_context[checkpoint][:,2:],np.full(len(f),checkpoint,dtype=float)])
            valid=mask&np.isfinite(features).all(axis=1)&np.isfinite(end_net)&np.isfinite(costsnow)
            # Restrict to states under water at the checkpoint; winner means positive
            # net terminal return, not knowledge available at decision time.
            distressed=valid&(side*cp-costsnow<0)
            trainids=np.flatnonzero(distressed&train)
            testids=np.flatnonzero(distressed&test)
            calids=np.flatnonzero(distressed&calibrate)
            rec={'index':r['index'],'side':r['side'],'checkpoint':checkpoint,
                'historical_distressed':len(trainids),'heldout_distressed':len(testids)}
            winners=trainids[end_net[trainids]>0];losers=trainids[end_net[trainids]<=0]
            rec['historical_recovered']=len(winners);rec['historical_failed']=len(losers)
            if min(len(winners),len(losers))<neighbors or len(testids)<20 or len(calids)<50:
                rec['status']='INSUFFICIENT_MATCH_SUPPORT';results.append(rec);continue
            scaler=StandardScaler().fit(features[trainids])
            trainx=scaler.transform(features[trainids]);testx=scaler.transform(features[testids]);calx=scaler.transform(features[calids])
            nn=NearestNeighbors(n_neighbors=neighbors,algorithm='auto').fit(trainx)
            caldist,calnear=nn.kneighbors(calx)
            calfrac=np.mean(end_net[trainids[calnear]]<=0,axis=1)
            caltruth=(end_net[calids]<=0)
            # Threshold is learned only from calibration, using precision gain
            # over the calibration unconditional failure rate; abstain if none.
            thresholds=np.arange(.5,.951,.05)
            eligible=[(float(np.mean(c[calfrac>=t])-np.mean(c)),float(t)) for t in thresholds for c in [caltruth] if np.sum(calfrac>=t)>=30]
            threshold=max(eligible)[1] if eligible and max(eligible)[0]>0 else None
            distances,near=nn.kneighbors(testx)
            nearids=trainids[near]
            frac=np.mean(end_net[nearids]<=0,axis=1)
            observed=(end_net[testids]<=0)
            baseline=float(np.mean(end_net[trainids]<=0))
            for eid,prob,truth,dist in zip(testids,frac,observed,distances.mean(axis=1)):
                predictions.append({'genome_index':r['index'],'checkpoint':checkpoint,'event_id':int(eid),'decision_date':str(dates.iloc[eid].date()),'failure_probability':float(prob),'baseline_probability':baseline,'failure_outcome':int(truth),'mean_neighbor_distance':float(dist),'calibrated_threshold':threshold})
            # No learned exit decision here; diagnostic classification only.
            rec.update(status='MATCHED_DIAGNOSTIC_UNCERTIFIED',
                calibrated_threshold=threshold,calibration_count=len(calids),
                historical_failure_rate=float(np.mean(end_net[trainids]<=0)),
                heldout_failure_rate=float(np.mean(observed)),
                mean_neighbor_failure_probability=float(np.mean(frac)),
                mean_match_distance=float(np.mean(distances)),
                ambiguous_fraction=float(np.mean((frac>=.3)&(frac<=.7))),
                high_failure_signal_fraction=float(np.mean(frac>=threshold)) if threshold is not None else None,
                high_failure_signal_false_exit_fraction=float(np.mean((frac>=threshold)&(~observed))) if threshold is not None else None,
                high_failure_signal_precision=float(np.mean(observed[frac>=threshold])) if threshold is not None and np.any(frac>=threshold) else None,
                high_failure_signal_recall=float(np.mean((frac>=threshold)[observed])) if threshold is not None and np.any(observed) else None)
            results.append(rec)
        pd.DataFrame(predictions).to_parquet(out/'heldout_event_predictions.parquet',index=False)
        with open(out/'results.jsonl','w') as dest:
            for row in results:dest.write(json.dumps(row,allow_nan=False)+'\n')
        (out/'progress.json').write_text(json.dumps({'genomes_done':len({r['index'] for r in results}),'genomes_requested':limit,'seconds':round(time.time()-start,1)}))
    manifest={'status':'MATCHED_WINNER_LOSER_CHECKPOINT_V3_UNCERTIFIED','scope':'DEV80 only',
        'genomes_evaluated':limit,'checkpoints':[5,10,15],'neighbors':neighbors,
        'train_before':'2016-01-01','calibration':'2016-07-15 through 2020-05-31','heldout_after':'2021-01-01',
        'limitations':['Only 20-session terminal labels','PIT market and security features aligned to checkpoint calendar; feature release-time audit still pending','No portfolio replay or parent promotion','Overlapping market episodes require cluster-aware validation','Calibration-only threshold descriptive, not a trading trigger'],
        'protected_banks_touched':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--limit',type=int,default=12);p.add_argument('--neighbors',type=int,default=25);args=p.parse_args();run(args.limit,args.neighbors)
