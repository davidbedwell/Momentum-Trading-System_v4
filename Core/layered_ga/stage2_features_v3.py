from __future__ import annotations

from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing as mp
import sys
import numpy as np
import pandas as pd

CERTIFIED_ROOT = Path(__file__).resolve().parents[2] / "Reconstruction/Certified-Stage2-Source-20261007"
DEV117_ROOT = Path('/home/ubuntu/mts-ga-dev117-permitted-20261006')

# Cross-sectional outputs created by the recovered factory after stock-local work.
CROSS_COLUMNS = (
    'return_252_percentile__v1','return_252_skip_20_percentile__v1','return_126_percentile__v1',
    'relative_volume_20_percentile__v1','natr_20_percentile__v1','realized_vol_20_percentile__v1',
    'sector_return_252_percentile__v1','breadth_above_sma_200__v1','breadth_positive_20__v1',
    'advance_decline_breadth__v1','new_high_low_breadth_252__v1','sector_vs_universe_return_63__v1',
    'relative_strength_change_20__v1',
)


def _source_factory():
    root=str(CERTIFIED_ROOT)
    if root not in sys.path: sys.path.insert(0,root)
    from MTS_V4.derived_feature_factory import build_predictor_rows
    return build_predictor_rows


def _raw_records(frame: pd.DataFrame, ticker: str, sector: str|None, industry: str|None):
    out=[]
    for r in frame.sort_values('date').itertuples(index=False):
        out.append({
            'security_id':ticker,'date':str(pd.Timestamp(r.date).date()),
            'open':float(r.open),'high':float(r.high),'low':float(r.low),'close':float(r.close),
            'volume':float(r.volume),'eligible':True,'ticker':ticker,
            'sector_id':sector,'industry_id':industry,
        })
    return out


def build_stock_local_frame(frame: pd.DataFrame, ticker: str, sector: str|None, industry: str|None) -> pd.DataFrame:
    rows=_source_factory()(_raw_records(frame,ticker,sector,industry))
    return pd.DataFrame(rows)


def _percentile(series: pd.Series) -> pd.Series:
    valid=series.notna(); out=pd.Series(np.nan,index=series.index,dtype=float)
    if not valid.any(): return out
    vals=series.loc[valid].astype(float); n=len(vals)
    if n==1: out.loc[valid]=1.0
    else: out.loc[valid]=(vals.rank(method='average')-1.0)/(n-1.0)
    return out


def recompute_cross_sectional(frame: pd.DataFrame) -> pd.DataFrame:
    d=frame.copy();d['effective_date']=pd.to_datetime(d['effective_date'])
    # Universe percentiles.
    for src,out in (
        ('return_252__v1','return_252_percentile__v1'),
        ('return_252_skip_20__v1','return_252_skip_20_percentile__v1'),
        ('return_126__v1','return_126_percentile__v1'),
        ('relative_volume_20__v1','relative_volume_20_percentile__v1'),
        ('natr_20__v1','natr_20_percentile__v1'),
        ('realized_vol_20__v1','realized_vol_20_percentile__v1')):
        d[out]=d.groupby('effective_date',sort=False,group_keys=False)[src].apply(_percentile)
    # Sector percentile; rows lacking a sector remain missing.
    d['sector_return_252_percentile__v1']=np.nan
    ok=d['sector_id'].notna() & d['sector_id'].ne('')
    if ok.any():
        d.loc[ok,'sector_return_252_percentile__v1']=(
            d.loc[ok].groupby(['effective_date','sector_id'],sort=False,group_keys=False)['return_252__v1'].apply(_percentile)
        )
    # Date-level breadth/market descriptors over eligible rows with a usable source value.
    def frac_positive(s):
        s=s.dropna(); return np.nan if len(s)==0 else float((s>0).mean())
    def advdec(s):
        s=s.dropna(); return np.nan if len(s)==0 else float(((s>0).sum()-(s<0).sum())/len(s))
    def nhnl(s):
        s=s.dropna(); return np.nan if len(s)==0 else float(((s>=1.0).sum()-(s<=0.0).sum())/len(s))
    g=d.groupby('effective_date',sort=False)
    maps={
        'breadth_above_sma_200__v1':g['close_to_sma_200__v1'].apply(frac_positive),
        'breadth_positive_20__v1':g['return_20__v1'].apply(frac_positive),
        'advance_decline_breadth__v1':g['return_1__v1'].apply(advdec),
        'new_high_low_breadth_252__v1':g['range_position_252__v1'].apply(nhnl),
    }
    for col,series in maps.items(): d[col]=d['effective_date'].map(series)
    median63=g['return_63__v1'].median();d['sector_vs_universe_return_63__v1']=d['return_63__v1']-d['effective_date'].map(median63)
    # 20-observation change in point-in-time 126-session percentile.
    d=d.sort_values(['security_id','effective_date']).reset_index(drop=True)
    d['relative_strength_change_20__v1']=d['return_126_percentile__v1']-d.groupby('security_id',sort=False)['return_126_percentile__v1'].shift(20)
    return d.sort_values(['effective_date','security_id']).reset_index(drop=True)


def _worker(args):
    file_path,sector,industry,out_path=args
    p=Path(file_path);ticker=p.stem;df=pd.read_parquet(p)
    out=build_stock_local_frame(df,ticker,sector,industry)
    out.to_parquet(out_path,index=False)
    return str(out_path),len(out)


def build_dev117_predictors(*, sector_metadata_path: Path, cache_dir: Path, workers: int=6) -> pd.DataFrame:
    cache_dir.mkdir(parents=True,exist_ok=True); final=cache_dir/'dev117_predictors_v3.parquet'
    if final.exists(): return pd.read_parquet(final)
    meta=json.loads(Path(sector_metadata_path).read_text());sm={r['ticker']:(r.get('sector'),r.get('industry')) for r in meta['rows']}
    local=cache_dir/'stock_local';local.mkdir(exist_ok=True)
    tasks=[]
    for p in sorted(DEV117_ROOT.glob('*.parquet')):
        sec,ind=sm.get(p.stem,(None,None));tasks.append((str(p),sec,ind,local/f'{p.stem}.parquet'))
    # forkserver/spawn avoids the unsafe post-thread fork failure mode from prior runs.
    ctx=mp.get_context('spawn')
    with ProcessPoolExecutor(max_workers=min(workers,len(tasks)),mp_context=ctx) as ex:
        list(ex.map(_worker,tasks))
    parts=[pd.read_parquet(t[3]) for t in tasks]
    d=recompute_cross_sectional(pd.concat(parts,ignore_index=True))
    d.to_parquet(final,index=False)
    return d
