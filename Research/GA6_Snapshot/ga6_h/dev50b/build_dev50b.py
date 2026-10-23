import json,sys,hashlib
from pathlib import Path
import pandas as pd,numpy as np
ROOT=Path('/opt/mts');OUT=ROOT/'ga6_h/dev50b';j=json.loads((OUT/'DEV50b_selection_manifest.json').read_text())
stock=[x['ticker'] for x in j['stocks']];sector={x['ticker']:x['sector'] for x in j['stocks']};industry={x['ticker']:x['industry'] for x in j['stocks']}
rawroot=ROOT/'thunder-migration/mts-v4-market-store-RECONSTRUCTED-20261004/raw_yfinance'
parts=[]
for t in stock:
 p=rawroot/(t+'.parquet')
 if not p.exists():raise FileNotFoundError(p)
 x=pd.read_parquet(p);x['ticker']=t
 parts.append(x)
raw=pd.concat(parts,ignore_index=True).sort_values(['date','ticker']);raw.to_parquet(OUT/'DEV50b_raw.parquet',index=False)
sys.path.insert(0,str(ROOT))
from ga5_redesign.canonical_engine import prepare
prepare(OUT/'DEV50b_raw.parquet',OUT/'DEV50b_base_features.parquet',sector_map=sector)
base=pd.read_parquet(OUT/'DEV50b_base_features.parquet')
layer=ROOT/'thunder-migration/mts-layered-run-20261007';sys.path.insert(0,str(layer))
from Core.layered_ga.stage2_features_v3 import build_stock_local_frame,recompute_cross_sectional,CROSS_COLUMNS
from ga5_redesign.ga4_registry import GA4_COLUMNS
features=[]
for t in stock:
 x=raw[raw.ticker==t].copy(); f=build_stock_local_frame(x,t,sector[t],industry[t]);features.append(f)
print('STOCK_FEATURES',len(features),flush=True)
pred=recompute_cross_sectional(pd.concat(features,ignore_index=True).drop(columns=list(CROSS_COLUMNS),errors='ignore'))
pred=pred.rename(columns={'effective_date':'date'})
cols=['date','ticker','security_id',*GA4_COLUMNS]
missing=set(cols)-set(pred.columns)
if missing:raise RuntimeError('Missing predictor columns: '+str(missing))
pred=pred[cols];base=base.merge(pred,on=['date','ticker','security_id'],how='left',validate='one_to_one',indicator=True)
if not base._merge.eq('both').all():raise ValueError('Unmatched feature rows')
base=base.drop(columns='_merge')
for name in GA4_COLUMNS:base['ga4_'+name]=np.tanh(pd.to_numeric(base.pop(name),errors='coerce').astype(float).clip(-1e8,1e8))
ref=pd.read_parquet(ROOT/'ga5_redesign/exploratory79_ga4_enriched.parquet')
base=base.drop(columns=['yahoo_symbol'],errors='ignore')
assert set(ref.columns)==set(base.columns),(set(ref.columns)-set(base.columns),set(base.columns)-set(ref.columns))
base=base[ref.columns];base.to_parquet(OUT/'DEV50b_enriched.parquet',index=False)
print('ENRICHED',len(base),base.ticker.nunique(),flush=True)
