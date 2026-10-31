#!/usr/bin/env python3
"""Fixed-calendar, strictly forward-looking technical signal test, 2019 and 2020."""
import csv,json,urllib.parse,urllib.request,datetime as dt,statistics,pathlib,math
root=pathlib.Path('/opt/mts/sector-leadership-independent')
members=list(csv.DictReader((root/'pilot_2019_sample.csv').open()))
start=int(dt.datetime(2017,1,1,tzinfo=dt.timezone.utc).timestamp())
end=int(dt.datetime(2021,1,1,tzinfo=dt.timezone.utc).timestamp())
prices={}
for r in members:
 s=r['symbol']
 try:
  u='https://query1.finance.yahoo.com/v8/finance/chart/'+s+'?'+urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d'})
  j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=16))['chart']['result'][0]
  prices[s]=[(dt.datetime.fromtimestamp(t,dt.timezone.utc).date(),float(v)) for t,v in zip(j['timestamp'],j['indicators']['adjclose'][0]['adjclose']) if v is not None]
  print('downloaded',s,len(prices[s]),flush=True)
 except Exception as e:print('FAIL',s,str(e)[:80],flush=True)
out=[]
for year in [2019,2020]:
 for quarter in range(1,5):
  begin=dt.date(year,1+3*(quarter-1),1)
  finish=dt.date(year+1,1,1) if quarter==4 else dt.date(year,1+3*quarter,1)
  for r in members:
   s=r['symbol']
   if s not in prices:continue
   hist=[p for date,p in prices[s] if date<begin]
   fut=[p for date,p in prices[s] if begin<=date<finish]
   if len(hist)<200 or len(fut)<35:continue
   p=hist[-1]
   # All signals are fixed at the previous trading close; future return is next quarter.
   m50=statistics.mean(hist[-50:]);m200=statistics.mean(hist[-200:])
   mom6=100*(p/hist[-127]-1) if len(hist)>=127 else float('nan')
   mom12=100*(p/hist[-252]-1) if len(hist)>=252 else float('nan')
   vol20=statistics.stdev(hist[i]/hist[i-1]-1 for i in range(len(hist)-19,len(hist)))*math.sqrt(252)*100
   fwd=100*(fut[-1]/fut[0]-1)
   out.append(dict(year=year,quarter=quarter,sector=r['sector'],symbol=s,asof=str(begin),fwd_return_pct=fwd,above50=int(p>m50),above200=int(p>m200),mom6_pct=mom6,mom12_pct=mom12,vol20_annual_pct=vol20))
for year in [2019,2020]:
 for quarter in range(1,5):
  for sector in sorted(set(r['sector'] for r in members)):
   g=sorted([r for r in out if r['year']==year and r['quarter']==quarter and r['sector']==sector],key=lambda r:r['fwd_return_pct'],reverse=True)
   for i,r in enumerate(g):r['future_group']='top' if i==0 else 'bottom' if i==len(g)-1 else 'middle'
print('RESULTS')
for year in [2019,2020]:
 print('YEAR',year)
 for group in ['top','middle','bottom']:
  g=[r for r in out if r['year']==year and r['future_group']==group]
  if not g:continue
  print(group,'n',len(g),'fwd',round(statistics.mean(r['fwd_return_pct'] for r in g),2),'above50',round(100*statistics.mean(r['above50'] for r in g),1),'above200',round(100*statistics.mean(r['above200'] for r in g),1),'mom6',round(statistics.mean(r['mom6_pct'] for r in g),2),'mom12',round(statistics.mean(r['mom12_pct'] for r in g),2),'vol20',round(statistics.mean(r['vol20_annual_pct'] for r in g),2))
for year in [2019,2020]:
 for field in ['mom6_pct','mom12_pct','above50','above200']:
  pairs=[]
  for q in range(1,5):
   for sector in sorted(set(r['sector'] for r in members)):
    g=[r for r in out if r['year']==year and r['quarter']==q and r['sector']==sector]
    if len(g)<5:continue
    hi=max(g,key=lambda r:r[field]);lo=min(g,key=lambda r:r[field])
    pairs.append(hi['fwd_return_pct']-lo['fwd_return_pct'])
  print('SIGNAL',year,field,'high_minus_low_forward_quarter_mean',round(statistics.mean(pairs),2) if pairs else 'NA','comparisons',len(pairs))
dest=root/'universe_2019'/'forward_quarter_signals_2019_2020.csv'
with dest.open('w',newline='') as f:
 fields=['year','quarter','sector','symbol','asof','future_group','fwd_return_pct','above50','above200','mom6_pct','mom12_pct','vol20_annual_pct']
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(out)
print('saved',dest,'rows',len(out))
