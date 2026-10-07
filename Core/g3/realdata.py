from __future__ import annotations
from pathlib import Path
import hashlib,json
import numpy as np,pandas as pd,yfinance as yf
ROOT=Path("/home/ubuntu/g3-independent-data")
RAW=ROOT/"raw_yfinance"; DERIVED=ROOT/"derived_v1"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def acquire(tickers,start,end):
    RAW.mkdir(parents=True,exist_ok=True)
    manifest={"source":"yfinance","start":start,"end":end,"tickers":list(tickers),"files":[]}
    for t in tickers:
        p=RAW/f"{t}.parquet"
        z=yf.download(t,start=start,end=end,auto_adjust=False,actions=False,progress=False,threads=False)
        if isinstance(z.columns,pd.MultiIndex): z.columns=z.columns.get_level_values(0)
        z.columns=[str(c).lower().replace(" ","_") for c in z.columns]
        z.index=pd.to_datetime(z.index).tz_localize(None)
        z.to_parquet(p)
        manifest["files"].append({"ticker":t,"path":str(p),"sha256":sha(p),"rows":len(z)})
    mp=ROOT/"acquisition_manifest.json";mp.write_text(json.dumps(manifest,indent=2)+"\n")
    return manifest
def derive(tickers):
    DERIVED.mkdir(parents=True,exist_ok=True); out={}
    for t in tickers:
        z=pd.read_parquet(RAW/f"{t}.parquet")
        a=z["adj_close"].astype(float) if "adj_close" in z else z["close"].astype(float)
        v=z["volume"].astype(float)
        f=pd.DataFrame(index=z.index)
        for n in (1,5,20,60,120): f[f"ret{n}"]=a.pct_change(n)
        f["dist_high20"]=a/a.rolling(20).max()-1
        f["ma_gap20"]=a/a.rolling(20).mean()-1
        f["ma_gap50"]=a/a.rolling(50).mean()-1
        r=a.pct_change();f["rv20"]=r.rolling(20).std(ddof=0)
        f["positive_day_fraction20"]=(r>0).rolling(20).mean()
        f["volume_rel20"]=v/v.rolling(20).mean()
        f["dollar_volume20"]=(a*v).rolling(20).mean()
        f=f.replace([np.inf,-np.inf],np.nan).dropna()
        p=DERIVED/f"{t}.parquet";f.to_parquet(p);out[t]={"path":str(p),"sha256":sha(p),"rows":len(f)}
    (ROOT/"derived_manifest.json").write_text(json.dumps(out,indent=2)+"\n");return out
def evidence_arrays(ticker,horizon=10):
    f=pd.read_parquet(DERIVED/f"{ticker}.parquet")
    z=pd.read_parquet(RAW/f"{ticker}.parquet")
    a=z["adj_close"].astype(float) if "adj_close" in z else z["close"].astype(float)
    f=f.loc[f.index.intersection(a.index)]
    X=((f-f.mean())/f.std(ddof=0).replace(0,1)).fillna(0).to_numpy(float)
    loc=a.index.get_indexer(f.index);Y=np.zeros((len(f),horizon),float)
    for i,k in enumerate(loc):
        base=float(a.iloc[k])
        for h in range(horizon):
            j=min(k+h+1,len(a)-1);Y[i,h]=float(a.iloc[j]/(base if h==0 else a.iloc[j-1])-1)
    return X,Y,list(f.columns)
