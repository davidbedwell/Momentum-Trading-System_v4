#!/usr/bin/env python3
"""Recover same-entity ticker-change candidates; never substitute acquiring-company histories."""
import csv,json,pathlib,urllib.parse,urllib.request
root=pathlib.Path(__file__).resolve().parent/'universe_2019'
rows=list(csv.DictReader((root/'price_coverage_2019.csv').open()))
missing={r['symbol'] for r in rows if r['status']!='available'}
# Manually reviewed as probable same issuer, not mergers. Treat as candidates pending independent identity audit.
aliases={'FB':'META','ANTM':'ELV','ABC':'COR','BLL':'BALL','CTL':'LUMN'}
out=[]
for old,new in aliases.items():
 if old not in missing:continue
 url='https://query1.finance.yahoo.com/v8/finance/chart/'+new+'?'+urllib.parse.urlencode({'period1':1546300800,'period2':1577836800,'interval':'1d'})
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  data=json.load(urllib.request.urlopen(req,timeout=15))['chart']['result'][0]
  vals=[v for v in data['indicators']['adjclose'][0]['adjclose'] if v is not None]
  dates=data['timestamp']
  out.append([old,new,len(vals),round(100*(vals[-1]/vals[0]-1),3) if len(vals)>200 else '', 'provisional_same_issuer_needs_mapping_validation'])
  print(old,new,len(vals),flush=True)
 except Exception as e:out.append([old,new,0,'','failed '+type(e).__name__])
with (root/'same_issuer_recovery_candidates.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['historical_symbol','queried_symbol','observations','adjusted_return_pct','status']);w.writerows(out)
print('candidate_recoveries',sum(x[2]>200 for x in out),flush=True)
