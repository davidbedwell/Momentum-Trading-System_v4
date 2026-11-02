import csv,urllib.request,urllib.parse,json,datetime,statistics,pathlib
root=pathlib.Path('/opt/mts/sector-leadership-independent')
rows=list(csv.DictReader((root/'pilot_2019_sample.csv').open()))
start=int(datetime.datetime(2018,1,1,tzinfo=datetime.timezone.utc).timestamp());end=int(datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc).timestamp())
out=[]
for r in rows:
 s=r['symbol']
 try:
  u='https://query1.finance.yahoo.com/v8/finance/chart/'+s+'?'+urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d'})
  j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=15))['chart']['result'][0]
  series=[(datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date(),v) for t,v in zip(j['timestamp'],j['indicators']['adjclose'][0]['adjclose']) if v is not None]
  ix=next(i for i,(date,_) in enumerate(series) if date.year==2019)
  v=[x[1] for x in series];p2019=v[ix:];prev=v[:ix]
  pre_6m=100*(prev[-1]/prev[-126]-1) if len(prev)>=126 else None
  pre_12m=100*(prev[-1]/prev[0]-1) if len(prev)>=200 else None
  above50=sum(v[i]>statistics.mean(v[i-49:i+1]) for i in range(ix,len(v)) if i>=49)/len(p2019)*100
  dreturns=[v[i]/v[i-1]-1 for i in range(ix+1,len(v))]
  vol=statistics.stdev(dreturns)*252**.5*100
  peak=p2019[0];mdd=0
  for z in p2019:
   peak=max(peak,z);mdd=min(mdd,100*(z/peak-1))
  out.append(dict(sector=r['sector'],symbol=s,annual_return=float(r['return_2019_pct']),eps=float(r['mean_eps_surprise_pct']),pre6=pre_6m,pre12=pre_12m,above50=above50,vol=vol,mdd=mdd))
  print(s,'pre6',round(pre_6m,1),'above50',round(above50,1),'vol',round(vol,1),'dd',round(mdd,1),flush=True)
 except Exception as e:print(s,'ERROR',str(e)[:90],flush=True)
for sector in sorted(set(r['sector'] for r in out)):
 g=sorted((r for r in out if r['sector']==sector),key=lambda r:r['annual_return'],reverse=True)
 for i,r in enumerate(g):r['group']='top' if i==0 else 'bottom' if i==len(g)-1 else 'middle'
print('SUMMARY')
for c in ['top','middle','bottom']:
 g=[r for r in out if r['group']==c]
 print(c,len(g),{k:round(statistics.mean(r[k] for r in g),2) for k in ['pre6','pre12','above50','vol','mdd']})
with (root/'universe_2019'/'pilot_technicals_2019.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['sector','symbol','group','annual_return','eps','pre6','pre12','above50','vol','mdd']);w.writeheader();w.writerows(out)
