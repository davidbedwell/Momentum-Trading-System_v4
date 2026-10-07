from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from Core.g3.earnings import classify_record,first_usable_session,event_features
from Core.g3.realdata import RAW,DERIVED,causal_zscore

EARNINGS_RAW=Path("/home/ubuntu/g3-independent-data/raw_eodhd_earnings/EODHD_EARNINGS_2006_2026.json")

def build_earnings_index(tickers:list[str],source:Path=EARNINGS_RAW)->dict[str,list[dict]]:
    wanted={f"{t}.US":t for t in tickers}
    with source.open() as f: rows=json.load(f)["earnings"]
    out={t:[] for t in tickers}
    for r in rows:
        t=wanted.get(r.get("code"))
        if t is not None and classify_record(r)=="ELIGIBLE": out[t].append(r)
    for t in out: out[t].sort(key=lambda r:(r["report_date"],r["date"]))
    return out

def earnings_daily_features(ticker:str,events:list[dict],sessions:pd.DatetimeIndex)->pd.DataFrame:
    cols=["earnings_actual","earnings_estimate","earnings_surprise_abs","earnings_surprise_percent","days_since_earnings"]
    f=pd.DataFrame(index=sessions,columns=cols,dtype=float)
    latest=None
    by_session={}
    for r in events:
        try: s=first_usable_session(r["report_date"],r.get("before_after_market"),sessions)
        except ValueError: continue
        by_session.setdefault(s,[]).append(r)
    for s in sessions:
        if s in by_session: latest=by_session[s][-1]
        if latest is not None:
            vals=event_features(latest)
            for k,v in vals.items(): f.at[s,k]=np.nan if v is None else v
            f.at[s,"days_since_earnings"]=(s-pd.Timestamp(latest["report_date"])).days
    return f

def evidence_arrays_with_earnings(ticker:str,events:list[dict],horizon:int=10,min_normalization_history:int=20):
    base=pd.read_parquet(DERIVED/f"{ticker}.parquet").sort_index()
    raw=pd.read_parquet(RAW/f"{ticker}.parquet").sort_index()
    a=raw["adj_close"].astype(float) if "adj_close" in raw else raw["close"].astype(float)
    base=base.loc[base.index.intersection(a.index)]
    ef=earnings_daily_features(ticker,events,base.index)
    f=base.join(ef)
    # Missing estimate-derived values remain neutral/missing; availability itself is represented by days_since.
    for c in ("earnings_actual","earnings_estimate","earnings_surprise_abs","earnings_surprise_percent"):
        f[c]=f[c].fillna(0.0)
    f["days_since_earnings"]=f["days_since_earnings"].fillna(9999.0)
    loc=a.index.get_indexer(f.index)
    eligible=(loc>=0)&((loc+horizon)<len(a))
    f=f.iloc[np.flatnonzero(eligible)]; loc=loc[eligible]
    norm=causal_zscore(f,min_periods=min_normalization_history)
    finite=norm.notna().all(axis=1).to_numpy()
    norm=norm.iloc[np.flatnonzero(finite)]; loc=loc[finite]
    X=norm.to_numpy(float); Y=np.empty((len(norm),horizon),float)
    for i,k in enumerate(loc):
        path=a.iloc[k:k+horizon+1].to_numpy(float); Y[i]=path[1:]/path[:-1]-1
    return X,Y,list(f.columns)
def aligned_evidence_with_earnings(tickers:list[str],events_by_ticker:dict[str,list[dict]],horizon:int=10,min_normalization_history:int=20):
    """Return strictly date-aligned evidence/outcomes for cross-sectional N2 nulls."""
    parts={}
    for ticker in tickers:
        base=pd.read_parquet(DERIVED/f"{ticker}.parquet").sort_index()
        raw=pd.read_parquet(RAW/f"{ticker}.parquet").sort_index()
        a=raw["adj_close"].astype(float) if "adj_close" in raw else raw["close"].astype(float)
        base=base.loc[base.index.intersection(a.index)]
        ef=earnings_daily_features(ticker,events_by_ticker[ticker],base.index)
        f=base.join(ef)
        for c in ("earnings_actual","earnings_estimate","earnings_surprise_abs","earnings_surprise_percent"):
            f[c]=f[c].fillna(0.0)
        f["days_since_earnings"]=f["days_since_earnings"].fillna(9999.0)
        loc=a.index.get_indexer(f.index)
        eligible=(loc>=0)&((loc+horizon)<len(a))
        f=f.iloc[np.flatnonzero(eligible)]; loc=loc[eligible]
        norm=causal_zscore(f,min_periods=min_normalization_history)
        finite=norm.notna().all(axis=1).to_numpy()
        norm=norm.iloc[np.flatnonzero(finite)]; loc=loc[finite]
        ys=[]
        for k in loc:
            path=a.iloc[k:k+horizon+1].to_numpy(float);ys.append(path[1:]/path[:-1]-1)
        parts[ticker]=(norm,pd.DataFrame(np.asarray(ys),index=norm.index))
    common=parts[tickers[0]][0].index
    for t in tickers[1:]: common=common.intersection(parts[t][0].index)
    common=common.sort_values()
    X=np.stack([parts[t][0].loc[common].to_numpy(float) for t in tickers],axis=1)
    Y=np.stack([parts[t][1].loc[common].to_numpy(float) for t in tickers],axis=1)
    return common,X,Y,list(parts[tickers[0]][0].columns)
