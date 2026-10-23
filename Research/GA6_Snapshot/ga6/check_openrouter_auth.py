import os,json,urllib.request,urllib.error
for endpoint in ['https://openrouter.ai/api/v1/auth/key','https://openrouter.ai/api/v1/credits']:
 req=urllib.request.Request(endpoint,headers={'Authorization':'Bearer '+os.environ['OPENROUTER_API_KEY']})
 try:
  with urllib.request.urlopen(req,timeout=20) as r:print(endpoint,'HTTP',r.status,'BODY',r.read(300).decode(errors='replace'))
 except urllib.error.HTTPError as e:print(endpoint,'HTTP',e.code,'BODY',e.read(300).decode(errors='replace'))
