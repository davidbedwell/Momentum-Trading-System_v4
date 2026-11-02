import json,urllib.request,urllib.parse,datetime,time,csv,pathlib,statistics
root=pathlib.Path('/opt/mts/sector-leadership-independent')
key=(root/'secrets/alphavantage.key').read_text().strip()
groups={'Technology':['AAPL','MSFT','NVDA','AMD','INTC'],'Healthcare':['JNJ','PFE','MRK','ABBV','UNH'],'Financials':['JPM','BAC','WFC','GS','C']}
rows=[]
for sector,symbols in groups.items():
 for symbol in symbols:
  row={'sector':sector,'symbol':symbol,'year':2019}
  try:
   start=int(datetime.datetime(2019,1,1,tzinfo=datetime.timezone.utc).timestamp())
   end=int(datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc).timestamp())
   url='https://query1.finance.yahoo.com/v8/finance/chart/'+symbol+'?'+urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d'})
   data=json.load(urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=15))['chart']['result'][0]
   adj=data['indicators'].get('adjclose',[{}])[0].get('adjclose',[])
   vals=[v for v in adj if v is not None]
   row['return_2019_pct']=round(100*(vals[-1]/vals[0]-1),2) if len(vals)>200 else None
   row['price_source']='Yahoo adjusted close (fallback; NOT Alpaca)'
  except Exception as e:row['price_error']=str(e)[:80]
  try:
   u='https://www.alphavantage.co/query?'+urllib.parse.urlencode({'function':'EARNINGS','symbol':symbol,'apikey':key})
   x=json.load(urllib.request.urlopen(u,timeout=18))
   q=[v for v in x.get('quarterlyEarnings',[]) if v.get('reportedDate','').startswith('2019-')]
   row['earnings_events_2019']=len(q)
   surprises=[]
   for v in q:
    try: surprises.append(float(v['surprisePercentage']))
    except (ValueError,TypeError,KeyError):pass
   row['mean_eps_surprise_pct']=round(statistics.mean(surprises),2) if surprises else None
   row['earnings_has_estimates']=sum(v.get('estimatedEPS') not in ('None',None,'') for v in q)
   if not x.get('quarterlyEarnings'):row['earnings_error']=str(x.get('Information',x.get('Note',x.get('Error Message','no earnings'))))[:120]
  except Exception as e:row['earnings_error']=str(e)[:80]
  rows.append(row)
  print(symbol,row.get('return_2019_pct'),row.get('earnings_events_2019'),row.get('mean_eps_surprise_pct'),flush=True)
for sector in groups:
 members=sorted([r for r in rows if r['sector']==sector and r.get('return_2019_pct') is not None],key=lambda r:r['return_2019_pct'],reverse=True)
 for i,r in enumerate(members):r['sample_rank']=i+1;r['sample_cohort']='top' if i==0 else 'bottom' if i==len(members)-1 else 'middle' if i==len(members)//2 else 'other'
out=root/'pilot_2019_sample.csv'
with out.open('w') as f:
 w=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in rows))));w.writeheader();w.writerows(rows)
print('WROTE',out,'records',len(rows))
