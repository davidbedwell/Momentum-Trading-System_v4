from pathlib import Path
import sys,gzip,json,hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
import pandas as pd
REPO=Path("/home/ubuntu/Momentum-Trading-System_v4")
OLD=REPO/"Reconstruction/Recovered-GitHub/october-original-code"
sys.path.insert(0,str(OLD))
from MTS_V4.earnings_event_features import build_earnings_event_rows,build_earnings_event_clock_rows
sys.path.pop(0);sys.path.insert(0,str(REPO))
from Core.conforming_ga.realdata import dev117,RAW_ROOT
NY=ZoneInfo("America/New_York")
CACHE=Path("/home/ubuntu/Downloads/MTS_EODHD_EARNINGS_20261006/raw-cache")
OUT=REPO/"Research/Data/PIT/earnings_events_published.parquet"
AUD=REPO/"Research/Data/PIT/earnings_events_published.audit.json"
tickers=set(dev117(REPO));docs=[]
for p in sorted(CACHE.glob("*.json.gz")):
    with gzip.open(p,"rt",encoding="utf-8") as h: doc=json.load(h)
    if doc.get("ticker") in tickers: docs.append(doc)
if {x["ticker"] for x in docs} != tickers: raise RuntimeError("DEV117 earnings cache incomplete")
events=[r for x in docs for r in x["rows"]]
closes={};sessions={}
for doc in docs:
    t=doc["ticker"];sid=doc["security_id"]
    x=pd.read_parquet(RAW_ROOT/f"{t}.parquet",columns=["date"])
    dates=tuple(sorted(pd.to_datetime(x["date"]).dt.date.unique()))
    closes[sid]=tuple(datetime(z.year,z.month,z.day,16,tzinfo=NY) for z in dates)
    sessions[sid]=tuple(z.isoformat() for z in dates)
event_rows=build_earnings_event_rows(events,market_close_times_by_security=closes)
clock_rows=build_earnings_event_clock_rows(event_rows,market_session_dates_by_security=sessions)
OUT.parent.mkdir(parents=True,exist_ok=True)
ticker_by_sid={x["security_id"]:x["ticker"] for x in docs}
out=pd.DataFrame(clock_rows)
out.insert(0,"ticker",out["security_id"].map(ticker_by_sid))
if out["ticker"].isna().any(): raise RuntimeError("security_id to ticker mapping incomplete")
out.to_parquet(OUT,index=False)
audit={"format":"MTS_CLEAN_ENGINE_PIT_EARNINGS_REGISTRY_V1",
"source":"recovered EODHD raw acquisition cache","universe":"DEV117 only",
"ticker_count":len(tickers),"source_event_rows":len(events),
"aligned_event_session_rows":len(event_rows),"published_clock_rows":len(clock_rows),
"first_effective_date":min(r["effective_date"] for r in clock_rows),
"last_effective_date":max(r["effective_date"] for r in clock_rows),
"unknown_timing_policy":"CONSERVATIVE_NEXT_OBSERVED_SESSION_CLOSE",
"sha256":hashlib.sha256(OUT.read_bytes()).hexdigest(),"passed":True}
AUD.write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
print(json.dumps(audit,indent=2,sort_keys=True))
