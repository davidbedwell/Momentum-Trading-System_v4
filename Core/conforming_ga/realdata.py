"""Permitted DEV117-only real-data loader and frozen fold registry."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
import pandas as pd, numpy as np

RAW_ROOT=Path("/home/ubuntu/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance")
FOLD_TEMPLATE=Path("Research/Reports/MTS_HORIZON_FREE_GA_FINAL_STUDY_FOLD{fold}_20261005.json")

class FoldIsolationError(RuntimeError): pass

def load_fold(repo:Path,fold:int):
    p=repo/FOLD_TEMPLATE.as_posix().format(fold=fold)
    j=json.loads(p.read_text())["result"]
    tr=tuple(j["train_tickers"]); bl=tuple(j["blind_tickers"])
    if len(tr)!=80 or len(bl)!=37 or set(tr)&set(bl): raise FoldIsolationError("80/37 integrity")
    return tr,bl

def dev117(repo:Path):
    u=set()
    for f in range(4):
        tr,bl=load_fold(repo,f);u.update(tr);u.update(bl)
    if len(u)!=117: raise FoldIsolationError(f"DEV union {len(u)}")
    return tuple(sorted(u))

def ticker_hash(tickers)->str:
    return hashlib.sha256("\n".join(tickers).encode()).hexdigest()

def build_permitted_mirror(repo:Path,dest:Path):
    allowed=dev117(repo);dest.mkdir(parents=True,exist_ok=True)
    for t in allowed:
        src=RAW_ROOT/f"{t}.parquet"
        if not src.is_file(): raise FileNotFoundError(src)
        out=dest/f"{t}.parquet"
        if not out.exists() or hashlib.sha256(out.read_bytes()).digest()!=hashlib.sha256(src.read_bytes()).digest():
            out.write_bytes(src.read_bytes())
    extra={p.stem for p in dest.glob("*.parquet")}-set(allowed)
    if extra: raise FoldIsolationError(f"extra tickers in permitted mirror: {sorted(extra)}")
    return allowed

class FoldLoader:
    def __init__(self,repo:Path,mirror:Path,fold:int,mode:str):
        tr,bl=load_fold(repo,fold)
        if mode not in ("train","blind"): raise ValueError(mode)
        self.tickers=tr if mode=="train" else bl
        self.forbidden=set(bl if mode=="train" else tr)
        self.mirror=mirror
    def load_prices(self):
        frames=[]
        for t in self.tickers:
            if t in self.forbidden: raise FoldIsolationError(t)
            p=self.mirror/f"{t}.parquet"
            if not p.is_file(): raise FileNotFoundError(p)
            x=pd.read_parquet(p,columns=["date","open","high","low","close","adj_close","dividends","volume"])
            x=x.assign(ticker=t)
            frames.append(x)
        out=pd.concat(frames,ignore_index=True)
        if set(out.ticker)&self.forbidden: raise FoldIsolationError("forbidden rows")
        return out
