from pathlib import Path
import json
import pandas as pd
from Core.layered_ga.ga4_stage1_context_join import attach_context
r=Path(__file__).resolve().parents[1]/'Research/Runs/layered'
s=r/'stage1-context-map-20261007';p=r/'stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'
d=pd.read_parquet(p,columns=['security_id','effective_date','sector_id'])
g=pd.read_parquet(s/'galaxy_context.parquet');z=pd.read_parquet(s/'sector_context.parquet')
o=attach_context(d,g,z)
summary={'rows':len(o),'galaxy_rows':int(o.galaxy_strength.notna().sum()),'sector_rows':int(o.sector_strength.notna().sum()),'galaxy_state_rows':int(o.galaxy_state.notna().sum()),'sector_state_rows':int(o.sector_state.notna().sum()),'sector_mapping':sorted(o[['sector_id','sector_etf']].drop_duplicates().astype(str).values.tolist()),'status':'METADATA_JOIN_AUDITED_NOT_PIT_CERTIFIED'}
print(json.dumps(summary,indent=2),flush=True)
