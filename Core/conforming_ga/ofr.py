"""Registered OFR FSI with conservative one-session publication lag."""
from pathlib import Path
import pandas as pd,numpy as np
from .availability import OFR_REL,OFR_SHA,file_sha
def load_ofr(repo:Path):
    p=repo/OFR_REL
    if file_sha(p)!=OFR_SHA:raise RuntimeError("OFR hash mismatch")
    d=pd.read_csv(p);d["Date"]=pd.to_datetime(d["Date"]);return d.sort_values("Date")
def ofr_asof(repo:Path,decision_date):
    d=load_ofr(repo);dt=pd.Timestamp(decision_date)
    x=d[d.Date<dt]  # at least next-session lag
    if x.empty:return np.nan
    return float(x.iloc[-1]["OFR FSI"])
