"""Research-only replay of GA5 frozen 13-center niche labels.
WARNING: centers were retrospectively adapted and are NOT certified for
point-in-time out-of-sample selection. Do not use for performance claims.
"""
import json
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path('/opt/mts/ga5_redesign')

def label_frame(frame, *, memory_path=None, centers_path=None):
    """Compute each day's label using trailing/current observations only.
    Returns one nearest center per stock-session and distances to all 13 centers.
    Model fit chronology is NOT established by this function.
    """
    memory=json.loads(Path(memory_path or ROOT/'chronological_memory_corrected_v2/memory.json').read_text())
    cp=json.loads(Path(centers_path or ROOT/'stocks31_40_corrected_v2/checkpoint.json').read_text())
    F=memory['features'];centers=np.asarray(cp['centers'],float)
    if centers.shape!=(13,len(F)):raise ValueError('center shape mismatch')
    if frame.duplicated(['ticker','date']).any():raise ValueError('duplicate symbol date')
    outputs=[]
    for ticker,g in frame.groupby('ticker',sort=True):
        g=g.sort_values('date').copy()
        v=g.adj_close.astype(float);delta=v.diff();flip=((np.sign(delta)*np.sign(delta.shift(1)))<0).astype(float)
        for w in (10,20,40):
            net=(v-v.shift(w)).abs()
            g[f'efficiency_{w}']=(net/delta.abs().rolling(w).sum()).clip(0,1)
            g[f'reversal_rate_{w}']=flip.rolling(w).mean()
            g[f'net_to_volatility_{w}']=net/(delta.abs().rolling(w).std()*np.sqrt(w))
        ratio=v/g.close.astype(float)
        g['range_width_20']=((g.high*ratio).rolling(20).max()-(g.low*ratio).rolling(20).min())/v
        g=g.replace([np.inf,-np.inf],np.nan)
        valid=g[F].notna().all(axis=1)
        if not valid.any():continue
        x=np.clip((g.loc[valid,F].to_numpy(float)-np.asarray(memory['median']))/np.asarray(memory['scale']),-5,5)
        dist=np.linalg.norm(x[:,None,:]-centers[None,:,:],axis=2)
        nearest=np.argmin(dist,axis=1)
        z=g.loc[valid,['date','ticker']].copy()
        z['research_niche']=[cp['ids'][i] for i in nearest]
        z['niche_distance']=dist[np.arange(len(nearest)),nearest]
        z['evidence_cutoff']=z.date
        z['certification']='RESEARCH_ONLY_RETROSPECTIVE_CENTERS'
        outputs.append(z)
    return pd.concat(outputs,ignore_index=True) if outputs else pd.DataFrame(columns=['date','ticker','research_niche','niche_distance','evidence_cutoff','certification'])
