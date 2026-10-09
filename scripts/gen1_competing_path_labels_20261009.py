"""Outcome-only recovery/failure competing-event labels for DEV80.
First passage after checkpoint to symmetric entry-notional 2% thresholds;
both-or-neither cases explicitly censored/ambiguous, not force-classified.
"""
import pathlib,json
import numpy as np,pandas as pd
ROOT=pathlib.Path('Research/Runs/gen1-merit-screen-20261008')
OUT=ROOT/'shared_path_store_20261009'
def main():
 a=np.load(ROOT/'phaseB_dev80_126_20261009/dev80_execution_arrays_126.npz',mmap_mode='r')
 ep=a['endpoint_return'][:,:20]
 n=len(ep)
 report={'status':'COMPETING_EVENT_LABELS_BUILT_UNCERTIFIED','scope':'DEV80','threshold_entry_notional':.02,'checkpoints':[5,10,15],'protected_banks_touched':False}
 for c in (5,10,15):
  # Use future executable opens ONLY as retrospective labels; no path labels in predictors.
  base=ep[:,c-1].astype(float)
  future=ep[:,c:20].astype(float)
  delta=future-base[:,None]
  finite=np.isfinite(delta)
  up=finite&(delta>=.02);down=finite&(delta<=-.02)
  first_up=np.where(up.any(axis=1),up.argmax(axis=1)+1,127)
  first_down=np.where(down.any(axis=1),down.argmax(axis=1)+1,127)
  label=np.where(first_up<first_down,1,np.where(first_down<first_up,-1,0)).astype('int8')
  # Side independent, encode directions in separate labels. Simultaneous impossible
  # for an open-only endpoint, but censored paths remain explicit.
  label[~np.isfinite(base)]=0
  result=pd.DataFrame({'event_id':np.arange(n,dtype=np.int32),'checkpoint':np.int8(c),
   'up_first':(label==1),'down_first':(label==-1),'censored_or_tied':(label==0),
   'up_first_sessions':np.where(first_up==127,-1,first_up).astype('int8'),
   'down_first_sessions':np.where(first_down==127,-1,first_down).astype('int8')})
  result.to_parquet(OUT/f'competing_path_labels_{c:02d}.parquet',index=False)
  report[str(c)]={'up_first':int((label==1).sum()),'down_first':int((label==-1).sum()),
   'censored':int((label==0).sum())}
 (OUT/'competing_path_labels_manifest.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
