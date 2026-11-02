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
    baseline = pd.Timestamp("2005-09-14")
    eligible = set(frame.loc[frame.date <= baseline,"ticker"])
    asof_counts = universe.loc[universe.index.intersection(eligible)].groupby("sector").size().reindex(sector_counts.index,fill_value=0)
    if (asof_counts == 0).any():
        raise ValueError("Missing a sector at historical cutoff")
    quotas = pd.Series(1,index=sector_counts.index,dtype=int)
    remaining = count-len(quotas)
    capacities = sector_counts-1
    while remaining:
        eligible_sectors = (quotas < asof_counts) & (quotas < sector_counts)
        if not eligible_sectors.any():
            raise ValueError("Insufficient sector capacity")
        # Largest deficit against proportional DEV79 representation.
        target = sector_counts / sector_counts.sum() * count
        sector = sorted(quotas.index[eligible_sectors],
                        key=lambda s:(-(target[s]-quotas[s]),s))[0]
        quotas[sector] += 1
        remaining -= 1
    picks = []
    for sector, quota in quotas.items():
        group = universe[universe.sector==sector].copy()
        # Deterministic as-of sampling; never rank by eventual survival.
        import random
        available = sorted(set(group.index) & eligible)
        if len(available) < int(quota):
            raise ValueError("Insufficient historically eligible stocks in "+sector)
        picks.extend(random.Random("dev32:20261025:"+sector).sample(available,int(quota)))
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
             "selection_method":"sector proportional quotas, as-of-2005-09-14 seeded selection",
             "warning":"Financial solvency is not verified; DEV79 itself may contain survivorship bias.",
             "universe_count":79,"selected_count":32,
             "sector_counts":{k:int(v) for k,v in counts.items()},
             "sector_quotas":{k:int(v) for k,v in quotas.items()},
             "asof_sector_counts":{k:int(v) for k,v in frame.loc[frame.date <= "2005-09-14"].groupby("sector_name").ticker.nunique().items()},
             "tickers":records}
    payload["selection_sha256"]=hashlib.sha256(json.dumps(records,sort_keys=True).encode()).hexdigest()
    Path(args.out).parent.mkdir(parents=True,exist_ok=True)
    Path(args.out).write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":payload["status"],"selected_count":32,
          "sector_quotas":payload["sector_quotas"],"selection_sha256":payload["selection_sha256"],
          "tickers":[r["ticker"] for r in records]},indent=2))
if __name__=="__main__":
    main()
