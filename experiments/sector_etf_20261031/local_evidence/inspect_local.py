"""Read-only local data admission audit; computes no strategy outcomes."""
import datetime, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[1]
paths=[Path('/opt/mts/thunder-migration/Momentum-Trading-System_v4/Research/Data/ExternalMarket/G2/legacy_sector_etf_panel_2005_2026.parquet'),Path('/opt/mts/thunder-migration/mts-layered-run-20261007/Research/Runs/layered/stage1-context-map-20261007/sector_etf_extension_xlre_xlc_yfinance_20261007.parquet'),Path('/opt/mts/ga6-git-backup/Research/Data/Comparators/SPY_YFINANCE_2005_2026.parquet')]
lock=json.loads((ROOT/'preregistration.lock.json').read_text())
assert hashlib.sha256((ROOT/'PREREGISTRATION.md').read_bytes()).hexdigest()==lock['sha256']
report={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'protocol_sha256':lock['sha256'],'network_requests':0,'outcomes_computed':False,'validation_outcomes_opened':False,'files':[]}
for p in paths:
 r={'path':str(p)}
 try:
  raw=p.read_bytes(); r['sha256']=hashlib.sha256(raw).hexdigest(); r['bytes']=len(raw)
  f=pq.ParquetFile(p);d=pd.read_parquet(p)
  r.update(status='readable',rows=len(d),columns=list(d.columns),schema=str(f.schema),metadata_keys=[k.decode() for k in (f.metadata.metadata or {})])
  if 'date' in d:
   dates=pd.to_datetime(d.date);r.update(first_date=str(dates.min()),last_date=str(dates.max()),duplicate_dates=int(dates.duplicated().sum()),dates_increasing=bool(dates.is_monotonic_increasing),rows_through_2025=int((dates<'2026-01-01').sum()))
  if 'adj_close' in d:
   a=d.adj_close;r.update(adjusted_close_nulls=int(a.isna().sum()),adjusted_close_nonpositive=int((a<=0).sum()),adjusted_close_nonfinite=int((~np.isfinite(a)).sum()))
  r['provenance_limit']='Filename identifies YFINANCE; explicit adj_close and dividends/splits fields exist. Embedded metadata identifies pandas/Arrow only; no acquisition URL/timestamp or adjustment guarantee verified.'
 except Exception as e:
  r.update(status='unreadable',error_type=type(e).__name__,errno=getattr(e,'errno',None),error=str(e))
 report['files'].append(r)
report['status']='BLOCKED_LOCAL_SECTOR_ACCESS' if any(r['status']=='unreadable' for r in report['files'][:2]) else 'LOCAL_FILES_READABLE'
(ROOT/'local_evidence/audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
