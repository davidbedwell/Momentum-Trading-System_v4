#!/usr/bin/env python3
"""Read-only real DEV80 path audit, no GA execution or heldout access."""
import json,sys,pathlib,hashlib
import numpy as np,pandas as pd
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from scripts.preflight_horizon_evolution_20261010 import PRED,ARRAY,BASE
from scripts.thirteen_window_crash_mask_20261011 import mask,HORIZONS
from Core.layered_ga.ga4_oracle_crash_mask import frozen_episode_intervals
EP=ROOT/'Research/Protocols/MTS_REENTRY_THREE_HYPOTHESIS_TEST_FREEZE_20261004.json'
frame=pd.read_parquet(PRED,columns=['effective_date','security_id'])
with np.load(ARRAY,allow_pickle=False,mmap_mode='r') as z:
 required=('endpoint_return','low_excursion','high_excursion','calendar_days','long_roundtrip','cluster_ids')
 shapes={k:list(z[k].shape) for k in required}
 if any(z[k].shape[0]!=len(frame) for k in required):raise RuntimeError('DEV80 row alignment failed')
 if any(z[k].shape[1]<65 for k in required if z[k].ndim==2):raise RuntimeError('64 horizon coverage failed')
calendar=pd.DatetimeIndex(pd.to_datetime(frame.effective_date)).normalize().unique().sort_values()
episodes=json.loads(EP.read_text())['episodes']
intervals=frozen_episode_intervals(calendar,episodes,10)
allowed=mask(frame.effective_date,calendar)
counts=allowed.sum(axis=0).tolist()
if any(n==0 for n in counts):raise RuntimeError('no eligible decisions for horizon')
# Critical: the historical oracle mask only establishes horizon eligibility.
# It does NOT prove that an executable multi-stock ledger implements
# liquidation, cash accrual, R-1 release, and position sizing.
report={'status':'BLOCKED_FULL_EXECUTION_CERTIFICATION','rows':len(frame),'trading_sessions':len(calendar),'array_shapes':shapes,'horizons':list(HORIZONS),'admissible_counts_by_horizon':counts,'excluded_intervals':[[str(a.date()),str(b.date())] for a,b in intervals],'verified':['DEV80_ROW_ALIGNMENT','64_HORIZON_FORWARD_ARRAY_COVERAGE','GA4_FROZEN_CRASH_INTERVALS','HORIZON_SPECIFIC_ELIGIBILITY'],'not_verified':['MULTI_STOCK_POSITION_LEDGER','HISTORICAL_TBILL_CASH_ACCRUAL','R1_CAUSAL_CONTROLLER_TAPE','MULTIPLE_TESTING_CALIBRATION','CRASH_BOUNDARY_LIQUIDATION_ON_REAL_PRICES','RESTART_RECOVERY'],'heldouts_accessed':False}
(BASE/'real_data_execution_preflight.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('admissible_counts_by_horizon','array_shapes')},indent=2))
