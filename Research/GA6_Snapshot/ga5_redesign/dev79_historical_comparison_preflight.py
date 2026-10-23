import json,glob,os,pandas as pd
from pathlib import Path
r=Path('/opt/mts/ga5_redesign');out=r/'dev79_historical_comparison_20261020';out.mkdir(exist_ok=True)
p=pd.read_parquet(r/'exploratory79_ga4_enriched.parquet');print('DEV79',len(p),p.ticker.nunique(),str(p.date.min()),str(p.date.max()))
models=['MTS_DISCOVERY_PORTFOLIO_CAPITAL_MITIGATION_FINAL_20261001.json','MTS_MOMENTUM_CONFIRMATION_ADDON_20261003.json','MTS_CRASH_STATE_GENOME_PIPELINE_20261003.json']
status=[]
for m in models:
 paths=glob.glob('/opt/mts/**/'+m,recursive=True)
 status.append({'model':m,'archived_reports':len(paths),'first_report':paths[0] if paths else None,'executable_model_verified':False,'run_status':'BLOCKED_MISSING_ORIGINAL_EXECUTABLE_MODEL'})
print('STATUS',status)
(out/'preflight.json').write_text(json.dumps({'universe':'DEV79 exploratory, not PIT certified','rows':len(p),'tickers':int(p.ticker.nunique()),'start':str(p.date.min()),'end':str(p.date.max()),'models':status,'ledger_schema':['strategy','ticker','signal_date','entry_date','entry_price','exit_date','exit_price','shares','fees','net_pnl','return_pct','holding_sessions','max_adverse_excursion_pct','max_favorable_excursion_pct','entry_niche','exit_niche','exit_reason'],'no_fabricated_results':True},indent=2))
