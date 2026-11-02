import pathlib,urllib.request,urllib.parse,json
p=pathlib.Path('/root/.config/mts/eodhd.env')
key=next(l.split('=',1)[1].strip().strip('"').strip("'") for l in p.read_text().splitlines() if l.startswith('EODHD_API_KEY='))
for symbol in ['ATVI.US','CELG.US','ABC.US','FB.US','EA.US','AAPL.US']:
 url='https://eodhd.com/api/eod/'+symbol+'?'+urllib.parse.urlencode({'api_token':key,'fmt':'json','from':'2019-01-01','to':'2019-12-31'})
 try:
  with urllib.request.urlopen(url,timeout=18) as r:
   b=r.read();j=json.loads(b);print(symbol,'HTTP',r.status,'rows',len(j) if isinstance(j,list) else 0,'message',str(j)[:100] if not isinstance(j,list) else '',flush=True)
 except Exception as e:print(symbol,type(e).__name__,str(e)[:80],flush=True)
