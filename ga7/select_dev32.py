"""Deterministic DEV32 sector-balanced discovery subset from DEV79.

Historical survival and financial solvency are audit flags, not inferred from
current listings or 2026 financials. Selection is provisional until PIT audit.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

def select_dev32(frame, count=32):
    frame = frame.copy()
    frame["date"] = pd.to_datetime(frame["date"])
    universe = frame.groupby("ticker").agg(
        sector=("sector_name", lambda x: x.mode().iloc[0]),
        first=("date","min"), last=("date","max"),
        sessions=("date","nunique"), median_price=("close","median"))
    if len(universe) != 79:
        raise ValueError("Expected exactly 79 DEV79 securities")
    sector_counts = universe.groupby("sector").size().sort_index()
    if len(sector_counts) > count:
        raise ValueError("Not enough slots for all sectors")
    quotas = pd.Series(1,index=sector_counts.index,dtype=int)
    remaining = count-len(quotas)
    capacities = sector_counts-1
    while remaining:
        eligible = capacities > (quotas-1)
        if not eligible.any():
            raise ValueError("Insufficient sector capacity")
        # Largest deficit against proportional DEV79 representation.
        target = sector_counts / sector_counts.sum() * count
        sector = sorted(quotas.index[eligible],
                        key=lambda s:(-(target[s]-quotas[s]),s))[0]
        quotas[sector] += 1
        remaining -= 1
    picks = []
    for sector, quota in quotas.items():
        group = universe[universe.sector==sector].copy()
        # Coverage first, then stable ticker ordering. No future returns used.
        group = group.sort_values(["sessions"],ascending=[False],kind="stable")
        group = group.reset_index().sort_values(
            ["sessions","ticker"],ascending=[False,True])
        picks.extend(group.head(int(quota))["ticker"].tolist())
    selected = universe.loc[sorted(picks)]
    if len(selected)!=count or selected.sector.nunique()!=len(sector_counts):
        raise AssertionError("Selection count/sector coverage mismatch")
    return selected,sector_counts,quotas

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    frame=pd.read_parquet(args.data,columns=["ticker","date","sector_name","close"])
    selected,counts,quotas=select_dev32(frame)
    records=[{"ticker":t,"sector":r.sector,"first_session":str(r["first"].date()),
              "last_session":str(r["last"].date()),"observed_sessions":int(r.sessions),
              "financial_solvency":"NOT_PIT_VERIFIED"}
             for t,r in selected.iterrows()]
    payload={"status":"PROVISIONAL_NOT_PIT_CERTIFIED",
             "selection_method":"sector proportional quotas, maximum observed coverage, ticker tie-break",
             "warning":"Full-period coverage selection uses future availability; historical survival and solvency not certified.",
             "universe_count":79,"selected_count":32,
             "sector_counts":{k:int(v) for k,v in counts.items()},
             "sector_quotas":{k:int(v) for k,v in quotas.items()},
             "tickers":records}
    payload["selection_sha256"]=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":payload["status"],"selected_count":32,
          "sector_quotas":payload["sector_quotas"],"selection_sha256":payload["selection_sha256"],
          "tickers":[r["ticker"] for r in records]},indent=2))
if __name__=="__main__":
    main()
