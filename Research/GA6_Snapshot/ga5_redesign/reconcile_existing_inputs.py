"""Reconcile preexisting sources; never infer historical index membership from price availability."""
import json,gzip,collections,datetime
from pathlib import Path
import pandas as pd
ROOT=Path('/opt/mts')
raw=pd.read_parquet(ROOT/'portfolio_evolution_dev80/dev80_raw_no_smci.parquet',columns=['date','ticker','security_id'])
archive=ROOT/'thunder-migration/Downloads/EODHD_US_EARNINGS_ARCHIVE_2006_2026/us_common_stock_earnings_2006_2026.jsonl.gz'
tickers=set(raw.ticker)
earnings=collections.defaultdict(set)
rows=0;matched=0;invalid=0
with gzip.open(archive,'rt') as f:
 for line in f:
  rows+=1
  try:
   rec=json.loads(line)
   t=str(rec.get('code','')).split('.')[0]
   ds=str(rec.get('report_date',''))[:10]
   datetime.date.fromisoformat(ds)
   if t in tickers:
    earnings[t].add(ds);matched+=1
  except (ValueError,TypeError,json.JSONDecodeError):
   invalid+=1
dates=pd.to_datetime(raw.date).dt.strftime('%Y-%m-%d')
sessions=sorted(set(dates))
sindex={d:i for i,d in enumerate(sessions)}
blocked={}
for ticker in sorted(tickers):
 embargo=set()
 for ds in earnings.get(ticker,set()):
  if ds in sindex:
   i=sindex[ds]
  else:
   import bisect
   i=bisect.bisect_left(sessions,ds)
  for j in (i-1,i,i+1):
   if 0<=j<len(sessions):embargo.add(sessions[j])
 blocked[ticker]=sorted(embargo)
report={
 'status':'SOURCE_RECONCILIATION_ONLY_NOT_PIT_CERTIFIED',
 'tickers':len(tickers),'price_rows':len(raw),'sessions':len(sessions),
 'earnings_archive_rows':rows,'earnings_rows_matching_79':matched,
 'invalid_earnings_rows':invalid,
 'tickers_with_earnings':len(earnings),
 'tickers_without_earnings':sorted(tickers-set(earnings)),
 'earnings_blackout_days_by_ticker':{k:len(v) for k,v in blocked.items()},
 'caveats':[
  'Report dates reconstructed from retrospective archive; publication/knowledge dates not verified',
  'The embargo includes the previous and next exchange session around each reported date',
  'No PIT index-membership authorization is inferred',
  'No historical PIT sector authorization is inferred',
  'No optimizer or trading simulation launched'
 ]
}
out=ROOT/'ga5_redesign/earnings_reconciliation_79.json'
out.write_text(json.dumps({'audit':report,'blocked':blocked},indent=2))
print(json.dumps(report,indent=2))
