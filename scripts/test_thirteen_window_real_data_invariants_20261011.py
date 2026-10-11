"""Read-only DEV80 invariants: no heldouts, no evolutionary evaluation."""
import json,pathlib,sys
import numpy as np,pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.preflight_horizon_evolution_20261010 import PRED,ARRAY
from scripts.thirteen_window_crash_mask_20261011 import mask
from scripts.thirteen_window_evolution_engine_20261011 import WINDOWS
frame=pd.read_parquet(PRED,columns=['effective_date','security_id'])
dates=pd.to_datetime(frame.effective_date)
assert dates.notna().all() and len(frame)>100000
with np.load(ARRAY,allow_pickle=False) as z:
 n=len(frame)
 for key in ('endpoint_return','low_excursion','high_excursion','calendar_days','long_roundtrip','short_roundtrip'):
  assert z[key].shape[0]==n and z[key].shape[1]>=65,(key,z[key].shape)
 assert len(z['cluster_ids'])==n
 # Check terminal horizons really differ in their data, not repeated 9-horizon columns.
 ret=z['endpoint_return']
 for h in (2,5,10,20,40,65):
  assert np.isfinite(ret[:,h-1]).sum()>1000
 assert not np.array_equal(ret[:,1],ret[:,64],equal_nan=True)
calendar=pd.DatetimeIndex(dates).normalize().unique().sort_values()
allowed=mask(dates,calendar)
assert allowed.shape==(len(frame),64)
assert any(not np.array_equal(allowed[:,h-2],allowed[:,h-1]) for h in range(3,66))
assert sum(hi-lo+1 for lo,hi in WINDOWS)==64
assert [h for lo,hi in WINDOWS for h in range(lo,hi+1)]==list(range(2,66))
print(json.dumps({'status':'PASS_REAL_DATA_INVARIANTS_ONLY','dev80_rows':len(frame),'horizons':64,'windows':len(WINDOWS),'heldouts_accessed':False}))
