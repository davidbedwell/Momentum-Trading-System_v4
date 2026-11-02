import csv,urllib.request,urllib.parse,json,datetime,statistics,pathlib
root=pathlib.Path('/opt/mts/sector-leadership-independent')
pilot=list(csv.DictReader((root/'pilot_2019_sample.csv').open()))
start=int(datetime.datetime(2019,1,1,tzinfo=datetime.timezone.utc).timestamp());end=int(datetime.datetime(2021,1,1,tzinfo=datetime.timezone.utc).timestamp())
out=[]
for r in pilot:
 s=r['symbol']
 try:
  u='https://query1.finance.yahoo.com/v8/finance/chart/'+s+'?'+urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d'})
  j=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=15))['chart']['result'][0]
  z=[(datetime.datetime.fromtimestamp(t,datetime.timezone.utc).date(),v) for t,v in zip(j['timestamp'],j['indicators']['adjclose'][0]['adjclose']) if v is not None]
  ix=next(i for i,(date,_) in enumerate(z) if date.year==2020)
  v=[x[1] for x in z];q=v[ix:];prev=v[:ix]
  if len(q)<150:raise ValueError('insufficient 2020 history')
  ret=100*(q[-1]/q[0]-1);pre6=100*(prev[-1]/prev[-126]-1);pre12=100*(prev[-1]/prev[0]-1)
  above50=100*sum(v[i]>statistics.mean(v[i-49:i+1]) for i in range(ix,len(v)) if i>=49)/len(q)
  dr=[v[i]/v[i-1]-1 for i in range(ix+1,len(v))]
  vol=statistics.stdev(dr)*252**.5*100
  peak=q[0];mdd=0
  for val in q:peak=max(peak,val);mdd=min(mdd,100*(val/peak-1))
  out.append(dict(sector=r['sector'],symbol=s,annual_return=ret,pre6=pre6,pre12=pre12,above50=above50,vol=vol,mdd=mdd))
  print(s,round(ret,1),flush=True)
 except Exception as e:print('ERROR',s,str(e)[:80],flush=True)
for sector in sorted(set(r['sector'] for r in out)):
 g=sorted((r for r in out if r['sector']==sector),key=lambda r:r['annual_return'],reverse=True)
 for i,r in enumerate(g):r['group']='top' if i==0 else 'bottom' if i==len(g)-1 else 'middle'
print('SUMMARY')
for c in ['top','middle','bottom']:
 g=[r for r in out if r['group']==c]
 print(c,len(g),{k:round(statistics.mean(r[k] for r in g),2) for k in ['annual_return','pre6','pre12','above50','vol','mdd']},flush=True)
with (root/'universe_2019'/'pilot_technicals_2020.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['sector','symbol','group','annual_return','pre6','pre12','above50','vol','mdd']);w.writeheader();w.writerows(out)
