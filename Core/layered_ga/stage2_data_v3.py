from __future__ import annotations
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd
from .stage2_features_v3 import DEV117_ROOT
from .stage2_path_v3 import ExecutionPaths,ProspectiveCosts,build_execution_paths,build_prospective_costs


def load_dev117_raw()->pd.DataFrame:
    parts=[]
    cols=['date','adj_close','close','high','low','open','volume','dividends','stock_splits']
    for p in sorted(DEV117_ROOT.glob('*.parquet')):
        d=pd.read_parquet(p,columns=cols);d['security_id']=p.stem;d['ticker']=p.stem;parts.append(d)
    out=pd.concat(parts,ignore_index=True);out['date']=pd.to_datetime(out.date)
    return out.sort_values(['date','security_id']).reset_index(drop=True)


def assert_predictor_alignment(raw:pd.DataFrame,predictors:pd.DataFrame)->None:
    if len(raw)!=len(predictors):raise ValueError(f'row-count mismatch raw={len(raw)} pred={len(predictors)}')
    rd=pd.to_datetime(raw.date).to_numpy(dtype='datetime64[D]');pdte=pd.to_datetime(predictors.effective_date).to_numpy(dtype='datetime64[D]')
    rs=raw.security_id.astype(str).to_numpy();ps=predictors.security_id.astype(str).to_numpy()
    if not np.array_equal(rd,pdte):
        i=int(np.flatnonzero(rd!=pdte)[0]);raise ValueError(f'date alignment mismatch at {i}: {rd[i]} != {pdte[i]}')
    if not np.array_equal(rs,ps):
        i=int(np.flatnonzero(rs!=ps)[0]);raise ValueError(f'security alignment mismatch at {i}: {rs[i]} != {ps[i]}')


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()


def build_path_cache(cache_dir:Path,predictor_path:Path)->dict:
    cache_dir.mkdir(parents=True,exist_ok=True);raw_path=cache_dir/'dev117_raw_aligned_v3.parquet'
    raw=load_dev117_raw();pred=pd.read_parquet(predictor_path,columns=['effective_date','security_id']);assert_predictor_alignment(raw,pred)
    if not raw_path.exists():raw.to_parquet(raw_path,index=False)
    p=build_execution_paths(raw,max_horizon=63);c=build_prospective_costs(raw,p)
    arrays={
      'endpoint_return':p.endpoint_return,'low_excursion':p.low_excursion,'high_excursion':p.high_excursion,'calendar_days':p.calendar_days,
      'long_roundtrip':c.long_roundtrip,'short_roundtrip':c.short_roundtrip,'spread_bps':c.spread_bps,'impact_bps':c.impact_bps,
      'adv_dollars':c.adv_dollars,'regulatory_sell_fraction':c.regulatory_sell_fraction,
    }
    files={}
    for name,a in arrays.items():
        fp=cache_dir/f'{name}.npy';np.save(fp,a,allow_pickle=False);files[name]={'file':fp.name,'shape':list(a.shape),'dtype':str(a.dtype),'sha256':sha256_file(fp),'bytes':fp.stat().st_size}
    meta={'format':'MTS_STAGE2_V3_PATH_CACHE_V1','rows':len(raw),'max_horizon':63,'alignment':'effective_date+security_id exact','predictor_file':str(predictor_path),'raw_file':raw_path.name,'files':files}
    (cache_dir/'path_cache_manifest.json').write_text(json.dumps(meta,indent=2));return meta


def load_path_cache(cache_dir:Path,mmap_mode:str='r')->tuple[ExecutionPaths,ProspectiveCosts]:
    ld=lambda n:np.load(cache_dir/f'{n}.npy',mmap_mode=mmap_mode,allow_pickle=False)
    p=ExecutionPaths(ld('endpoint_return'),ld('low_excursion'),ld('high_excursion'),ld('calendar_days'))
    c=ProspectiveCosts(ld('long_roundtrip'),ld('short_roundtrip'),ld('spread_bps'),ld('impact_bps'),ld('adv_dollars'),ld('regulatory_sell_fraction'))
    return p,c
