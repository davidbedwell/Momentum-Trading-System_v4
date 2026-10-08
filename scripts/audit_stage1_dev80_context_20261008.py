from pathlib import Path
import json,hashlib
import pandas as pd
r=Path(__file__).resolve().parents[1]/'Research/Runs/layered'
s=r/'stage1-context-map-20261007'; p=r/'stage2-opportunity-v3-20261007/ga4_dev80_checkpoint/dev80_predictors.parquet'
g=pd.read_parquet(s/'galaxy_context.parquet'); z=pd.read_parquet(s/'sector_context.parquet'); d=pd.read_parquet(p,columns=['security_id','effective_date','sector_id','eligible'])
for x in (g,z): x['date']=pd.to_datetime(x.date)
d['effective_date']=pd.to_datetime(d.effective_date)
assert g.date.is_unique and not z.duplicated(['date','context_key']).any()
joined=d.merge(g[['date','state','strength','trajectory','rv20']].rename(columns={'date':'effective_date','state':'galaxy_state'}),on='effective_date',how='left',validate='many_to_one',indicator=True)
sector_names=sorted(d.sector_id.dropna().unique().tolist()); sector_keys=sorted(z.context_key.dropna().unique().tolist())
result={'predictor_rows':len(d),'eligible_rows':int(d.eligible.sum()),'galaxy_exact_date_matches':int((joined._merge=='both').sum()),'galaxy_exact_date_match_fraction':float((joined._merge=='both').mean()),'galaxy_nonnull_state_rows':int(joined.galaxy_state.notna().sum()),'predictor_min_date':str(d.effective_date.min().date()),'galaxy_min_date':str(g.date.min().date()),'predictor_sector_names':sector_names,'stage1_sector_keys':sector_keys,'sector_key_namespace_matches':set(sector_names)==set(sector_keys),'source_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (s/'galaxy_context.parquet',s/'sector_context.parquet',p)},'decision':'NOT_CERTIFIED_UNTIL_CAUSAL_SECTOR_MAPPING_AND_COVERAGE_VERIFIED'}
print(json.dumps(result,indent=2),flush=True)
