#!/usr/bin/env python3
import sys,json,gzip,pickle,hashlib,os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import pandas as pd, pyarrow.parquet as pq
ROOT=Path('/home/ubuntu/Momentum-Trading-System_v4')
sys.path.insert(0,str(ROOT/'Reconstruction/Recovered-GitHub/october-original-code'))
sys.path.insert(0,str(ROOT/'Reconstruction/Recovered-GitHub/october-original-code/scripts'))
from MTS_V4.derived_feature_factory import build_matured_outcome_rows
from run_one_ticker_computational_search import _run_family,EXECUTABLE_FAMILIES
from MTS_V4.search_candidate_analysis import _compile_signal
RAW=Path('/home/ubuntu/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance')
PRED='/home/ubuntu/mts-v4-nexus-derived-market-current-sp500-calibration-20260915-RECONSTRUCTED-CLEAN/data/sp500-current-calibration-20260915__a0dd6a1a76bb/mts_market_predictors_v2__3e9bdc71246a/predictor-v2-initial-20260929-predictors-2005-09-14-2026-09-14.parquet'
OUT=Path('/home/ubuntu/mts-v4-preserved50-search-reconstructed-20261005'); OUT.mkdir(exist_ok=True)
SIDMAP={str(x).rsplit('_',1)[-1]:str(x) for x in pq.read_table(PRED,columns=['security_id']).column(0).unique().to_pylist()}
report=json.load(open(ROOT/'Research/Reports/MTS_HELDOUT_50_FOUR_ERA_PORTFOLIO_20261002.json'))
TICKERS=sorted(report['coverage'].keys())
def one(t):
    op=OUT/f'{t}_COMPUTATIONAL_SEARCH_RECONSTRUCTED_20261005.json'
    if op.exists(): return t,'RESUMED'
    raw=pq.read_table(RAW/f'{t}.parquet').to_pylist()
    sid=SIDMAP[t]
    for r in raw:
        r['security_id']=sid; r['date']=str(r['date'])[:10]; r['ticker']=t; r['eligible']=True
    outcomes=list(build_matured_outcome_rows(raw))
    tab=pq.read_table(PRED,filters=[('security_id','=',sid)])
    predictors=tab.to_pylist()
    for r in predictors:r['effective_date']=str(r['effective_date'])[:10]
    evidence=f'RECONSTRUCTED_PRESERVED50|{sid}|predictors:v2|outcomes:v1'
    fams={}
    for fam in EXECUTABLE_FAMILIES:
        fid,res=_run_family(family_id=fam,ticker=t,predictors=predictors,outcomes=outcomes,evidence_identity=evidence,budget=500,seed=20260930)
        fams[fid]=res
    payload={'format':'MTS_V4_ONE_SUBJECT_COMPUTATIONAL_SEARCH_RECONSTRUCTED_V1','ticker':t,'security_id':sid,'cohort':'PRESERVED50_RECONSTRUCTED',
      'predictor_feature_set_version':'v2','outcome_feature_set_version':'v1','budget_per_family_per_optimizer':500,'seed':20260930,
      'families':fams,'provenance':'RECONSTRUCTED_FROM_SURVIVING_SPEC','finalist_aware_tuning':False}
    op.write_text(json.dumps(payload,indent=2,sort_keys=True,default=str)+'\n')
    return t,'COMPLETE'
if __name__=='__main__':
    print('TICKERS',len(TICKERS),flush=True)
    with ProcessPoolExecutor(max_workers=6) as ex:
        fs={ex.submit(one,t):t for t in TICKERS}
        for i,f in enumerate(as_completed(fs),1):
            t,s=f.result(); print(f'[{i}/{len(TICKERS)}] {s}={t}',flush=True)
