#!/usr/bin/env python3
import csv,json,pathlib,urllib.parse,urllib.request,time,datetime
ROOT=pathlib.Path(__file__).resolve().parent
KEY=(ROOT/'secrets/alphavantage.key').read_text().strip()
CSV=ROOT/'pilot_2019_sample.csv'
CACHE=ROOT/'earnings_cache';CACHE.mkdir(exist_ok=True)
rows=list(csv.DictReader(CSV.open()))
pending=[r for r in rows if r['earnings_events_2019']=='0']
print('pending',len(pending),flush=True)
batch=pending[:5]
for r in batch:
 symbol=r['symbol']; url='https://www.alphavantage.co/query?'+urllib.parse.urlencode({'function':'EARNINGS','symbol':symbol,'apikey':KEY})
 try:
  with urllib.request.urlopen(url,timeout=25) as resp: data=json.load(resp)
  if 'quarterlyEarnings' not in data:
   print(symbol,'LIMITED',str(data.get('Information',data.get('Note',data.get('Error Message','unknown'))))[:120],flush=True)
   break
  q=[x for x in data['quarterlyEarnings'] if x.get('reportedDate','').startswith('2019-')]
  (CACHE/(symbol+'.json')).write_text(json.dumps(data))
  values=[]
  for x in q:
   try:values.append(float(x['surprisePercentage']))
   except (ValueError,KeyError,TypeError):pass
  r['earnings_events_2019']=str(len(q));r['earnings_has_estimates']=str(sum(x.get('estimatedEPS') not in ('None',None,'') for x in q))
  r['mean_eps_surprise_pct']=str(round(sum(values)/len(values),2)) if values else ''
  r['earnings_error']=''
  print(symbol,'OK','2019 events',len(q),flush=True)
 except Exception as e:print(symbol,'ERROR',type(e).__name__,str(e)[:100],flush=True);break
 time.sleep(1.2)
with CSV.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('saved',sum(int(r['earnings_events_2019'])>0 for r in rows),'of',len(rows),'stocks',flush=True)
