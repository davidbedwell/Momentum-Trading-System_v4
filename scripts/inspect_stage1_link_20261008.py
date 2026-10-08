from pathlib import Path
import pandas as pd
r=Path(__file__).resolve().parents[1]/'Research/Runs/layered'
for f in [r/'stage1-context-map-20261007/galaxy_context.parquet',r/'stage1-context-map-20261007/sector_context.parquet',r/'stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet']:
 d=pd.read_parquet(f)
 print(f.name,len(d),list(d.columns),d.head(1).to_dict('records'),flush=True)
