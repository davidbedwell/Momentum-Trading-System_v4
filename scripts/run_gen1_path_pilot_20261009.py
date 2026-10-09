"""DEV80 causal checkpoint-exit research pilot. Not a certification or portfolio simulation."""
import argparse, json, pathlib, time, hashlib
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import brier_score_loss, roc_auc_score
from Core.layered_ga.ga4_causal_compiler import CausalSignalCompiler
P=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
D=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
def finite(x):return bool(np.isfinite(x))
def run(limit):
    start=time.time();out=P/'recovery_failure_pilot_20261009';out.mkdir(exist_ok=True)
    frame=pd.read_parquet(D/'dev80_predictors.parquet')
    arrays=np.load(P/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz',mmap_mode='r')
    candidates=[json.loads(s) for s in open(P/'all_candidates.jsonl')]
    assert len(candidates)==4360
    compiler=CausalSignalCompiler(frame)
    dates=pd.to_datetime(frame.effective_date)
    # 126-calendar-day embargo exceeds 20-session outcomes; avoids boundary leakage.
    t1=pd.Timestamp('2016-01-01');t2=pd.Timestamp('2021-01-01')
    embargo=pd.Timedelta(days=190)
    records=[]
    for r in candidates[:limit]:
        idx=r['index'];side=1 if r['side']=='LONG' else -1
        mask=np.logical_and.reduce([compiler.compile(f,g) for f,g in r['chromosomes']])
        base=arrays['endpoint_return'][:,19];cp=arrays['endpoint_return'][:,4]
        low=arrays['low_excursion'][:,3];high=arrays['high_excursion'][:,3]
        cost=arrays['long_roundtrip'] if side==1 else arrays['short_roundtrip']
        base_net=side*base-cost[:,19];cp_net=side*cp-cost[:,4]
        # Observed by T+6 open: 5-session endpoint and preceding 4-session extremes.
        x=np.column_stack([side*cp,side*low,side*high,side*(high-low),np.full(len(frame),side)])
        valid=mask & np.isfinite(x).all(axis=1)&np.isfinite(base_net)&np.isfinite(cp_net)
        tr=np.flatnonzero(valid&(dates<t1-embargo));cal=np.flatnonzero(valid&(dates>=t1)&(dates<t2-embargo));te=np.flatnonzero(valid&(dates>=t2))
        rec={'index':idx,'side':r['side'],'train_n':len(tr),'calibration_n':len(cal),'test_n':len(te)}
        if min(len(tr),len(cal),len(te))<100:
            rec['status']='INSUFFICIENT_CHRONOLOGICAL_SUPPORT';records.append(rec);continue
        # Label is incremental future benefit of holding, not retrospective trade winner.
        y=(base_net<cp_net).astype(int)
        if len(np.unique(y[tr]))<2:
            rec['status']='ONE_CLASS_TRAIN';records.append(rec);continue
        model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=200,class_weight=None))
        model.fit(x[tr],y[tr])
        pc=model.predict_proba(x[cal])[:,1]
        # Threshold selection on calibration only; no test selection or test fitting.
        # Choose economically best candidate among coarse prespecified thresholds.
        thresholds=np.arange(.35,.901,.05)
        gain=cp_net[cal]-base_net[cal]
        improvements=[float(np.mean((pc>=t)*gain)) for t in thresholds]
        best=int(np.argmax(improvements));threshold=float(thresholds[best])
        pt=model.predict_proba(x[te])[:,1];ex=pt>=threshold
        outcome=np.where(ex,cp_net[te],base_net[te])
        rec.update(status='PILOT_OUT_OF_TRAINING',threshold=threshold,calibration_improvement=float(improvements[best]),test_baseline_mean_net=float(np.mean(base_net[te])),test_path_mean_net=float(np.mean(outcome)),test_incremental_mean_net=float(np.mean(outcome-base_net[te])),test_exit_fraction=float(np.mean(ex)),test_brier=float(brier_score_loss(y[te],pt)),test_auc=float(roc_auc_score(y[te],pt)) if len(np.unique(y[te]))==2 else None)
        records.append(rec)
        with open(out/'results.jsonl','w') as f:
            for row in records:f.write(json.dumps(row,allow_nan=False)+'\n')
        (out/'progress.json').write_text(json.dumps({'completed':len(records),'requested':limit,'elapsed_seconds':round(time.time()-start,1)}))
    manifest={'status':'CAUSAL_PATH_PILOT_UNCERTIFIED','candidates_total':len(candidates),'evaluated':len(records),'requested':limit,'train_cutoff':'2016-01-01','calibration_start':'2016-01-01','test_start':'2021-01-01','embargo_days':190,'horizon_sessions':20,'checkpoint_sessions':5,'limitations':['single checkpoint, not full dynamic exit policy','trade-level net EV only, not portfolio CAGR/MDD','reused historical paths may have cross-security episode dependence','no episode bootstrap or multiple-testing adjustment','threshold grid predeclared in script, calibration optimized','not a parent selection gate'],'protected_banks_touched':False,'gen2_authorized':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2),flush=True)
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--limit',type=int,default=12);args=a.parse_args();run(args.limit)
