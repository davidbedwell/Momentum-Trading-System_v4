from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import hashlib,json
import pandas as pd

@dataclass(frozen=True)
class EarningsEvent:
    code:str
    report_date:str
    fiscal_date:str
    before_after_market:str|None
    currency:str|None
    actual:float|None
    estimate:float|None
    difference:float|None
    percent:float|None

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def load_raw(path:Path)->tuple[dict,list[dict]]:
    with path.open() as f: payload=json.load(f)
    if payload.get("type")!="Earnings" or not isinstance(payload.get("earnings"),list):
        raise ValueError("unexpected EODHD earnings payload")
    return {k:v for k,v in payload.items() if k!="earnings"},payload["earnings"]

def classify_record(r:dict)->str:
    rd=pd.Timestamp(r["report_date"]); fd=pd.Timestamp(r["date"])
    if rd < fd: return "QUARANTINE_REPORT_BEFORE_FISCAL_DATE"
    if r.get("before_after_market") not in (None,"BeforeMarket","AfterMarket"):
        return "QUARANTINE_UNKNOWN_MARKET_TIMING_VALUE"
    return "ELIGIBLE"

def first_usable_session(report_date:str,before_after_market:str|None,sessions:pd.DatetimeIndex)->pd.Timestamp:
    """Conservative PIT clock for daily-close evidence.

    BeforeMarket may affect that report-date session if it is a trading day.
    AfterMarket and unknown timing are unavailable until the next trading session.
    """
    d=pd.Timestamp(report_date).normalize()
    sessions=pd.DatetimeIndex(sessions).normalize().sort_values().unique()
    side="left" if before_after_market=="BeforeMarket" else "right"
    i=sessions.searchsorted(d,side=side)
    if i>=len(sessions): raise ValueError("no usable session after report date")
    return pd.Timestamp(sessions[i])

def event_features(r:dict)->dict:
    """Raw earnings primitives only; no named strategy or outcome label."""
    actual=r.get("actual"); estimate=r.get("estimate")
    surprise=None
    if actual is not None and estimate is not None:
        surprise=float(actual)-float(estimate)
    return {
        "earnings_actual":None if actual is None else float(actual),
        "earnings_estimate":None if estimate is None else float(estimate),
        "earnings_surprise_abs":surprise,
        "earnings_surprise_percent":None if r.get("percent") is None else float(r["percent"]),
    }
