import json,gzip,datetime,bisect,collections,pathlib
import numpy as np
import pandas as pd
from ga5_redesign.ga4_registry import GA4_COLUMNS
from ga5_redesign.canonical_engine import digest_file
root=pathlib.Path('/opt/mts');p=root/'thunder-migration/mts-certification-20261011/dev87'
a=pd.read_parquet(p/'dev87_ga6_base_features.parquet')
b=pd.read_parquet(p/'dev87_predictors.parquet',columns=['effective_date','ticker','security_id',*GA4_COLUMNS]).rename(columns={'effective_date':'date'})
z=a.merge(b,on=['date','ticker','security_id'],validate='one_to_one',indicator=True)
assert z._merge.eq('both').all()
z.drop(columns='_merge',inplace=True)
for c in GA4_COLUMNS:z['ga4_'+c]=np.tanh(pd.to_numeric(z.pop(c),errors='coerce').clip(-1e8,1e8).astype(float))
out=p/'dev87_ga6_enriched.parquet';z.to_parquet(out,index=False)
print('ENRICHED',len(z),z.ticker.nunique(),flush=True)
archive=root/'thunder-migration/Downloads/EODHD_US_EARNINGS_ARCHIVE_2006_2026/us_common_stock_earnings_2006_2026.jsonl.gz'
tickers=set(z.ticker);earnings=collections.defaultdict(set)
with gzip.open(archive,'rt') as f:
 for line in f:
  r=json.loads(line);t=str(r.get('code','')).split('.')[0];d=str(r.get('report_date',''))[:10]
  if t in tickers:
   try:datetime.date.fromisoformat(d);earnings[t].add(d)
   except ValueError:pass
sessions=sorted({str(x)[:10] for x in z.date});blocked={}
for t in sorted(tickers):
 embargo=set()
 for d in earnings[t]:
  i=bisect.bisect_left(sessions,d)
  for j in (i-1,i,i+1):
   if 0<=j<len(sessions):embargo.add(sessions[j])
 blocked[t]=sorted(embargo)
policy={'membership':[[str(d)[:10],t,True] for d,t in z[['date','ticker']].itertuples(index=False,name=None)],'risk_veto':{d:True for d in sessions},'blocked':blocked,'cash_proxy_annual_yield':0.03}
(p/'dev87_ga6_policy.json').write_text(json.dumps(policy,separators=(',',':')))
report={'source':'DEV87 frozen manifest','rows':len(z),'tickers':len(tickers),'missing_earnings_tickers':sorted(tickers-set(earnings)),'feature_sha256':digest_file(out),'policy_sha256':digest_file(p/'dev87_ga6_policy.json'),'status':'EXPLORATORY HOLDOUT ONLY; PIT membership and earnings publication timing not certified; permissive risk veto'}
(p/'dev87_ga6_preflight.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
