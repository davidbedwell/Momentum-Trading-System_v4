"""Fail-closed point-in-time split and 63-session embargo for Gen1 path studies."""
import numpy as np
import pandas as pd
def split_mask(dates,calendar,begin=None,end=None,purge=63):
    d=pd.to_datetime(dates).to_numpy(dtype='datetime64[ns]')
    cal=np.asarray(pd.to_datetime(calendar).sort_values().unique(),dtype='datetime64[ns]')
    if len(cal)==0 or len(np.unique(cal))!=len(cal):raise ValueError('Invalid calendar')
    pos=np.searchsorted(cal,d)
    if np.any(pos>=len(cal)) or np.any(cal[np.minimum(pos,len(cal)-1)]!=d):raise ValueError('Dates not on calendar')
    lo=0 if begin is None else int(np.searchsorted(cal,np.datetime64(begin)))
    hi=len(cal) if end is None else int(np.searchsorted(cal,np.datetime64(end)))
    if not 0<=lo<hi<=len(cal):raise ValueError('Invalid split')
    # Require every label to mature before the next split boundary.
    return (pos>=lo)&(pos+purge<hi)
def validate_assignment(row):
    from Core.layered_ga.gen1_horizon_path_labels import ORIGINAL_HORIZONS,valid_checkpoints
    h=row.get('horizon')
    if h is None:
        if row.get('status')!='INSUFFICIENT_TRAIN_SUPPORT':raise ValueError('Unassigned without status')
        return ()
    if h not in ORIGINAL_HORIZONS:raise ValueError('Nonoriginal horizon')
    cps=valid_checkpoints(h)
    if tuple(row.get('checkpoints',()))!=cps:raise ValueError('Incorrect checkpoints')
    if row.get('status')!='TRAIN_ONLY_HORIZON_PROVISIONAL_UNCERTIFIED':raise ValueError('Uncertified horizon status mismatch')
    return cps
