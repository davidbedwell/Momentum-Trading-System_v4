"""Join historical GA4 predictor archive to 79-ticker exploratory GA5 features."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
sys.path.insert(0,'/opt/mts')
from ga5_redesign.ga4_registry import SOURCE,GA4_COLUMNS
from ga5_redesign.canonical_engine import digest_file
root=Path('/opt/mts/ga5_redesign')
base=root/'exploratory79_features.parquet'
f=pd.read_parquet(base)
p=pd.read_parquet(SOURCE,columns=['effective_date','ticker','security_id',*GA4_COLUMNS])
p=p.rename(columns={'effective_date':'date'})
if p.duplicated(['date','ticker','security_id']).any():raise ValueError('Ambiguous historical predictor identity')
f=f.merge(p,on=['date','ticker','security_id'],how='left',validate='one_to_one',indicator=True)
if not f._merge.eq('both').all():raise ValueError('Unmatched GA4 predictor rows')
f=f.drop(columns=['_merge'])
for name in GA4_COLUMNS:
 x=pd.to_numeric(f.pop(name),errors='coerce').astype(float)
 # Stable fixed, point-in-time-independent squashing: avoids fitting normalization
 # on future observations. Preserve raw value for provenance in original archive.
 f['ga4_'+name]=np.tanh(x.clip(-1e8,1e8))
out=root/'exploratory79_ga4_enriched.parquet'
f.to_parquet(out,index=False)
meta=json.loads(base.with_suffix('.manifest.json').read_text())
meta['ga4_archive_sha256']=digest_file(SOURCE)
meta['ga4_predictors']=len(GA4_COLUMNS)
meta['research_only']='GA4 predictor values retrospectively archived; not independently PIT certified'
out.with_suffix('.manifest.json').write_text(json.dumps(meta,indent=2))
print(json.dumps({'rows':len(f),'tickers':f.ticker.nunique(),'ga4_features':len(GA4_COLUMNS),'columns':len(f.columns),'output':str(out),'sha256':digest_file(out)},indent=2))
