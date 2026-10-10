"""Connect PIT A/B/C/R-1 signals from Parquet to the existing controller.

This is an adapter, NOT a detector. It refuses to invent missing signals.
A/B/C and R-1 must already be computed causally and independently.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from .defensive_daily_replay import DayRecord,replay
from .regime_state_routing import normal_entry_eligibility,defensive_transition_closes

REQUIRED=("date","A","B","C","R1")

def controller_from_parquet(path, *, expected_sha256=None):
    p=Path(path)
    if p.suffix.lower()!=".parquet":raise ValueError("controller input must be Parquet")
    if expected_sha256 is not None:
        import hashlib
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        if digest!=expected_sha256:raise ValueError("Parquet SHA256 mismatch")
    frame=pd.read_parquet(p)
    missing=[c for c in REQUIRED if c not in frame.columns]
    if missing:raise ValueError("missing independently computed PIT signals: "+",".join(missing))
    if "B1" not in frame.columns:frame["B1"]=False
    dates=pd.to_datetime(frame["date"],errors="raise")
    if dates.isna().any() or dates.dt.tz is not None:raise ValueError("invalid dates")
    day=dates.dt.strftime("%Y-%m-%d")
    if day.duplicated().any() or not day.is_monotonic_increasing:raise ValueError("date ordering")
    for key in ("A","B","B1","C","R1"):
        if frame[key].isna().any() or not frame[key].map(lambda x: isinstance(x,(bool,np.bool_))).all():
            raise ValueError("missing/nonboolean signal: "+key)
    records=[DayRecord(str(d),bool(a),bool(b),bool(c),bool(r),bool(b1))
             for d,a,b,c,r,b1 in zip(day,frame.A,frame.B,frame.C,frame.R1,frame.B1)]
    rows=replay(records)
    controller_dates=np.asarray([r["date"] for r in rows],dtype="datetime64[D]")
    controller_states=np.asarray([r["state"] for r in rows])
    return rows,controller_dates,controller_states

def route_from_parquet(path,decision_dates,*,expected_sha256=None):
    rows,dates,states=controller_from_parquet(path,expected_sha256=expected_sha256)
    return {"declarations":rows,
            "normal_entries_allowed":normal_entry_eligibility(decision_dates,dates,states),
            "defensive_transition_closes":defensive_transition_closes(dates,states)}