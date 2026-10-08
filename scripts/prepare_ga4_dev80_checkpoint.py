"""Prepare DEV80-only immutable inputs for GA4; never read DEV37 stock files."""
import json,hashlib,sys
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007'
MANIFEST=ROOT/'Research/Partitions/GA4_DEV80_DEV37_FROZEN_SPLIT.json'
OUT=BASE/'ga4_dev80_checkpoint'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    m=json.loads(MANIFEST.read_text());allowed=set(m['DEV80']);sealed=set(m['DEV37'])
    if len(allowed)!=80 or len(sealed)!=37 or allowed&sealed:raise ValueError('invalid freeze')
    raw=pd.read_parquet(BASE/'cache/dev117_raw_aligned_v3.parquet')
    raw=raw.loc[raw.security_id.astype(str).isin(allowed)].copy()
    if set(raw.security_id.astype(str))!=allowed:raise ValueError('raw coverage')
    stock=[]
    for sid in sorted(allowed):
        f=BASE/'cache/stock_local'/f'{sid}.parquet'
        if not f.is_file():raise FileNotFoundError(f)
        x=pd.read_parquet(f)
        if set(x.security_id.astype(str))!={sid}:raise ValueError('stock identity mismatch')
        stock.append(x)
    OUT.mkdir(parents=True,exist_ok=True)
    from Core.layered_ga.ga4_fold_isolation import freeze_fold_membership
    from Core.layered_ga.ga4_fold_predictors import rebuild_fold_predictors
    from Core.layered_ga.stage2_features_v3 import CROSS_COLUMNS
    fold=freeze_fold_membership(m['DEV80'],m['DEV37'])
    predictors,scope=rebuild_fold_predictors(pd.concat(stock,ignore_index=True).drop(columns=list(CROSS_COLUMNS),errors="ignore"),fold,'DEV80')
    raw_file=OUT/'dev80_raw.parquet';pred_file=OUT/'dev80_predictors.parquet'
    if raw_file.exists() or pred_file.exists():raise FileExistsError('checkpoint already exists; refuse overwrite')
    raw.to_parquet(raw_file,index=False);predictors.to_parquet(pred_file,index=False)
    report={'membership_sha256':sha(MANIFEST),'membership_digest':fold['membership_sha256'],
            'raw_sha256':sha(raw_file),'predictors_sha256':sha(pred_file),
            'rows_raw':len(raw),'rows_predictors':len(predictors),'securities':len(allowed),
            'predictor_scope':scope,'dev37_opened':False,'search_started':False,
            'status':'DEV80_INPUT_CHECKPOINT_NOT_CANDIDATE_SELECTION'}
    (OUT/'checkpoint_manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
