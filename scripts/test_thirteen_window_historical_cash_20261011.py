#!/usr/bin/env python3
"""Actual DEV80 session dates + historical Treasury source alignment smoke."""
import json,pathlib,sys
import numpy as np,pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.preflight_horizon_evolution_20261010 import PRED
from scripts.thirteen_window_cash_rate_20261011 import session_cash_returns,DEFAULT
f=pd.read_parquet(PRED,columns=['effective_date'])
cal=pd.DatetimeIndex(pd.to_datetime(f.effective_date)).normalize().unique().sort_values()
r=session_cash_returns(cal)
assert len(r)==len(cal) and np.isfinite(r).all()
assert (r>-.01).all() and (r<.01).all()
raw=pd.read_csv(DEFAULT)
assert len(raw)>1000
print(json.dumps({'status':'PASS_HISTORICAL_CASH_SOURCE_ALIGNMENT_ONLY','sessions':len(cal),'source_rows':len(raw),'min_daily':float(r.min()),'max_daily':float(r.max()),'cash_proxy_not_total_return':True,'portfolio_economics_certified':False}))
