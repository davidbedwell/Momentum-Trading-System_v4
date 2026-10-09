"""Build reusable DEV80-only event/checkpoint store, without genome selection or fitting."""
import json,time,hashlib,pathlib,argparse
import numpy as np,pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
SOURCE=pathlib.Path('Research/Runs/layered/stage2-opportunity-v3-20261007/ga4_dev80_checkpoint')
FEATURES=('return_5__v1','return_20__v1','close_to_sma_50__v1','close_to_sma_200__v1','breadth_above_sma_200__v1')
def build(out,checkpoints):
    start=time.time();out.mkdir(parents=True,exist_ok=True)
    f=pd.read_parquet(SOURCE/'dev80_predictors.parquet')
    a=np.load(ROOT/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz',mmap_mode='r')
    assert len(f)==a['endpoint_return'].shape[0]
    assert not f.duplicated(['security_id','effective_date']).any()
    # Past-only decision-date features. Future checkpoint returns are separate outcome data.
    observed=['security_id','effective_date','sector_id']+[k for k in FEATURES if k in f.columns]
    f[observed].to_parquet(out/'decision_features.parquet',index=False)
    n=len(f);eid=np.arange(n,dtype=np.int32)
    # At checkpoint c the T+1+c open is observed. Outcome is subsequent T+1+20 open.
    # Checkpoint features here are past-path endpoint returns only; intraday extremes
    # are deliberately excluded pending precise timestamp audit.
    for c in checkpoints:
        assert 1<=c<20
        d=pd.DataFrame({'event_id':eid,'checkpoint':np.full(n,c,dtype=np.int8),
          'checkpoint_gross_return':a['endpoint_return'][:,c-1],
          'continuation_gross_return':a['endpoint_return'][:,19]-a['endpoint_return'][:,c-1],
          'long_exit_cost_at_20':a['long_roundtrip'][:,19],
          'short_exit_cost_at_20':a['short_roundtrip'][:,19],
          'long_exit_cost_at_checkpoint':a['long_roundtrip'][:,c-1],
          'short_exit_cost_at_checkpoint':a['short_roundtrip'][:,c-1]})
        d.to_parquet(out/f'checkpoint_{c:02d}.parquet',index=False)
    manifest={'status':'SHARED_EVENT_STORE_BUILT_UNCERTIFIED','scope':'DEV80','rows':n,'checkpoints':checkpoints,
       'decision_feature_columns':observed,'time_seconds':round(time.time()-start,2),
       'source':'phaseB 126-session execution arrays','causality_note':'decision_features are PIT at T; checkpoint return known only at T+1+c open; continuation is outcome-only, NEVER predictor',
       'no_parent_selection_changes':True,'protected_banks_touched':False}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    print(json.dumps(manifest),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--checkpoints',type=int,nargs='+',default=[5,10,15]);a=p.parse_args()
    build(ROOT/'shared_path_store_20261009',a.checkpoints)
