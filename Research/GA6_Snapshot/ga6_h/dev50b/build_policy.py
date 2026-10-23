import json,gzip,collections,bisect
from pathlib import Path
import pandas as pd
root=Path('/opt/mts');out=root/'ga6_h/dev50b'
raw=pd.read_parquet(out/'DEV50b_raw.parquet',columns=['date','ticker'])
tickers=set(raw.ticker);sessions=sorted(pd.to_datetime(raw.date).dt.strftime('%Y-%m-%d').unique());si={d:i for i,d in enumerate(sessions)}
earnings=collections.defaultdict(set)
archive=root/'thunder-migration/Downloads/EODHD_US_EARNINGS_ARCHIVE_2006_2026/us_common_stock_earnings_2006_2026.jsonl.gz'
with gzip.open(archive,'rt') as f:
 for line in f:
  try:
   r=json.loads(line);t=str(r.get('code','')).split('.')[0];d=str(r.get('report_date',''))[:10]
   if t in tickers and len(d)==10:earnings[t].add(d)
  except (ValueError,TypeError,json.JSONDecodeError):pass
blocked={}
for t in sorted(tickers):
 days=set()
 for d in earnings[t]:
  i=si.get(d,bisect.bisect_left(sessions,d))
  for k in (i-1,i,i+1):
   if 0<=k<len(sessions):days.add(sessions[k])
 blocked[t]=sorted(days)
policy={'membership':[[str(d)[:10],t,True] for d,t in raw[['date','ticker']].itertuples(index=False,name=None)],'risk_veto':{d:True for d in sessions},'blocked':blocked,'cash_proxy_annual_yield':0.03}
(out/'DEV50b_policy.json').write_text(json.dumps(policy,separators=(',',':')))
print('POLICY',len(tickers),'SESSIONS',len(sessions),'EARNINGS_TICKERS',len(earnings),'BLACKOUTS',sum(map(len,blocked.values())),flush=True)
