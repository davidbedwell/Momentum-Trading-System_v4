import json,hashlib
from pathlib import Path
from collections import Counter
import pandas as pd
root=Path('/opt/mts');part=root/'thunder-migration/Momentum-Trading-System_v4/Research/Partitions/MTS_V4_REPAIRED_UNTOUCHED_PARTITION_A100_B100_DISCOVERY136_20261007.json'
j=json.loads(part.read_text());meta=pd.read_csv(root/'thunder-migration/Momentum-Trading-System_v4/Reconstruction/Manifests/mts-v4-current-sp500-calibration-20260915.RECONSTRUCTED.csv')
sector=dict(zip(meta.ticker,meta.sector_id));industry=dict(zip(meta.ticker,meta.industry_id))
a=set(pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet',columns=['ticker']).ticker)
b=set(pd.read_parquet(root/'thunder-migration/mts-certification-20261011/dev87/dev87_ga6_enriched.parquet',columns=['ticker']).ticker)
protected={x['ticker'] for x in j['VERIFICATION_A']+j['VERIFICATION_B']};touched=set(j['audit']['touched_tickers']);pool={x['ticker'] for x in j['DISCOVERY_UNTOUCHED']}-a-b-protected-touched
assert len(pool)==136 and not pool&(a|b|protected|touched)
reference=Counter(sector[t] for t in a|b);count=Counter();selected=[];remaining=set(pool)
while len(selected)<50:
 candidates=sorted(remaining,key=lambda t:(-((50*reference[sector[t]]/len(a|b))-count[sector[t]]),hashlib.sha256(('DEV50b-20261023-'+t).encode()).hexdigest()))
 t=candidates[0];selected.append(t);remaining.remove(t);count[sector[t]]+=1
out=root/'ga6_h/dev50b';out.mkdir(exist_ok=True)
manifest={'name':'DEV50b','status':'FROZEN_SELECTION_PENDING_DATA_PREFLIGHT','selection_rule':'greedy sector-proportional quotas against DEV79+DEV87, SHA256 deterministic tie break; no performance data','seed':'DEV50b-20261023','source_partition':str(part),'source_sha256':hashlib.sha256(part.read_bytes()).hexdigest(),'period_start':'2019-01-01','period_end_exclusive':'2025-01-01','stock_count':50,'reference_count':len(a|b),'reference_sector_mix':dict(reference),'selected_sector_mix':dict(count),'stocks':[{'ticker':t,'sector':sector[t],'industry':industry[t]} for t in selected],'excluded_prior_groups':len(a|b),'excluded_protected_A_B':len(protected),'candidate_pool_count':len(pool),'limitations':['Historical 2019-2024 time period already researched','Current 2026 survivor universe; not point-in-time survivorship-free','Original partition labels unexposed for GA6, not proof of never studied anywhere']}
(out/'DEV50b_selection_manifest.json').write_text(json.dumps(manifest,indent=2));print('SELECTED',len(selected),'SECTORS',dict(count));print('TICKERS',','.join(selected));print('MANIFEST',out/'DEV50b_selection_manifest.json')
