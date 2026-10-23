"""Actual data-duration gate. No invented regime classifications."""
import json
from pathlib import Path
import pandas as pd
from ga6.structural_independent_v2_20261022.validation_governance import InformationHorizon,assess_splits
source=Path('/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet')
dates=sorted(set(pd.read_parquet(source,columns=['date']).date.astype(str)))
dates=[d for d in dates if '2005-09-14'<=d<'2026-09-15']
horizon=InformationHorizon(40,160,0)
result=assess_splits(dates,{},horizon)
report={'dataset':'DEV79 exploratory; PIT membership unverified','dates':len(dates),'start':dates[0],'end':dates[-1],'assumed_lookback_sessions':160,'state_carry_sessions':'UNKNOWN: must derive from engine','result':result,'certifiable':False}
path=Path('/opt/mts/ga6/governance/GA6_SPLIT_FEASIBILITY_PROBE_20261021.json');path.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
