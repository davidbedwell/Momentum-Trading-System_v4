import pathlib,urllib.parse,urllib.request,json
k=(pathlib.Path('/opt/mts/sector-leadership-independent/secrets/businessquant.key').read_text().strip())
for tick in ['AAPL','ATVI','CELG','ABC','FB']:
 u='https://data.businessquant.com/quotes?'+urllib.parse.urlencode({'ticker':tick,'mode':'eod','from_date':'2019-01-01','till_date':'2019-12-31','limit':5,'api_key':k})
 try:
  with urllib.request.urlopen(u,timeout=18) as r:
   x=json.load(r);m=x.get('metadata',{}) if isinstance(x,dict) else {};print(tick,'http',r.status,'ticker',m.get('ticker'),'company',m.get('companyname'),'records',m.get('pagination',{}).get('total_records'),'data',len(x.get('data',[])) if isinstance(x,dict) else '?','keys',list(x)[:5],flush=True)
 except Exception as e:print(tick,type(e).__name__,str(e)[:70],flush=True)
