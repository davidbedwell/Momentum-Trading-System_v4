#!/usr/bin/env python3
"""Independent 2019 historical membership and preliminary price coverage audit."""
import pathlib,urllib.request,yaml,csv,json,datetime,concurrent.futures,time
root=pathlib.Path(__file__).resolve().parent
out=root/'universe_2019';out.mkdir(exist_ok=True)
source='https://raw.githubusercontent.com/shardul0701/SP500-Survivorship-bias-data-2004-2026/main/src/sp500_ticker_history/sp500-ticker-changes-2019.yaml'
raw=urllib.request.urlopen(source,timeout=30).read();(out/'membership_2019_source.yaml').write_bytes(raw)
data=yaml.safe_load(raw)
members=sorted(set(data['tickers_on_Jan_1']))
print('2019 initial members',len(members),'change dates',len(data.get('changes',{})),flush=True)
with (out/'members_2019_start.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['symbol','membership_date','source']);w.writerows((s,'2019-01-01',source) for s in members)
start=int(datetime.datetime(2019,1,1,tzinfo=datetime.timezone.utc).timestamp())
end=int(datetime.datetime(2020,1,1,tzinfo=datetime.timezone.utc).timestamp())
def one(symbol):
 try:
  q=urllib.parse.urlencode({'period1':start,'period2':end,'interval':'1d'})
  u='https://query1.finance.yahoo.com/v8/finance/chart/'+symbol.replace('.','-')+'?'+q
  req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
  data=json.load(urllib.request.urlopen(req,timeout=12))['chart']['result'][0]
  vals=[v for v in data['indicators'].get('adjclose',[{}])[0].get('adjclose',[]) if v is not None]
  if len(vals)<150:return (symbol,'insufficient',len(vals),'','')
  return (symbol,'available',len(vals),round(100*(vals[-1]/vals[0]-1),3),'')
 except Exception as e:return (symbol,'unavailable',0,'',str(e)[:90])
import urllib.parse
results=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 for i,row in enumerate(pool.map(one,members),1):
  results.append(row)
  if i%100==0:print('processed',i,'available',sum(x[1]=='available' for x in results),flush=True)
with (out/'price_coverage_2019.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['symbol','status','daily_points','adj_return_pct','error']);w.writerows(results)
print('COMPLETE',len(results),'available',sum(x[1]=='available' for x in results),'unavailable',sum(x[1]=='unavailable' for x in results),'insufficient',sum(x[1]=='insufficient' for x in results),flush=True)
