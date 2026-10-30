import csv,json,pathlib,urllib.request,urllib.parse,datetime
p=pathlib.Path('/opt/mts/sector-leadership-independent/universe_2019')
rows=list(csv.DictReader((p/'price_coverage_2019.csv').open()))
aliases={'FB':'META','ANTM':'ELV','ABC':'COR','CBS':'PARA','DISCA':'WBD','DISCK':'WBD','CTL':'LUMN','INFO':'SPGI','KSU':'CP','MXIM':'ADI','BLL':'BALL','HFC':'DINO','FLIR':'TDY','CERN':'ORCL','NBL':'CVX','CXO':'COP','ALXN':'AZN','AGN':'ABBV','CELG':'BMY','ETFC':'MS','APC':'OXY','DWDP':'DD','ATVI':'MSFT'}
def get(sym):
 url='https://query1.finance.yahoo.com/v8/finance/chart/'+sym+'?'+urllib.parse.urlencode({'period1':1546300800,'period2':1577836800,'interval':'1d'})
 req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
 x=json.load(urllib.request.urlopen(req,timeout=12))['chart']['result'][0]
 return [v for v in x['indicators'].get('adjclose',[{}])[0].get('adjclose',[]) if v is not None]
out=[]
for r in rows:
 if r['status']=='available':continue
 s=r['symbol'];a=aliases.get(s)
 if not a:continue
 try:
  vals=get(a)
  status='candidate_continuous_rename' if s in ['FB','ANTM','ABC','CBS','CTL','HFC','BLL'] else 'acquisition_or_reorganization_NOT_VALID_RETURN'
  out.append([s,a,status,len(vals),round(100*(vals[-1]/vals[0]-1),2) if len(vals)>150 else ''])
  print(s,a,status,len(vals),flush=True)
 except Exception as e:out.append([s,a,'unavailable',0,''])
with (p/'alias_probe_2019.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['historical_symbol','current_symbol_candidate','classification','bars','candidate_return_pct']);w.writerows(out)
print('Alias candidates',len(out),'with data',sum(x[3]>150 for x in out),flush=True)
