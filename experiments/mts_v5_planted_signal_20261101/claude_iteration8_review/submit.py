#!/usr/bin/env python3
"""Authorized OpenRouter submission; credentials stay in memory, never output."""
import os,json,re,shlex,hashlib,datetime,urllib.request,urllib.error,time,socket
from pathlib import Path
O=Path(__file__).resolve().parent
URL='https://openrouter.ai/api/v1/chat/completions'
SECRET=Path('/opt/mts/thunder-migration/.openrouter_api_env')
def open_retry(request,timeout):
 for attempt in range(1,4):
  try:return urllib.request.urlopen(request,timeout=timeout)
  except urllib.error.URLError as e:
   transient=isinstance(e.reason,(socket.gaierror,TimeoutError)) or 'Temporary failure in name resolution' in str(e.reason)
   if not transient or attempt==3:raise
   meta.setdefault('transient_retries',[]).append({'attempt':attempt,'error_type':type(e.reason).__name__})
   time.sleep(2**attempt)

now=lambda:datetime.datetime.now(datetime.timezone.utc).isoformat()
meta={'timestamp_utc':now(),'endpoint':URL,'submitted':False,'http_status':None,'model':None,'usage':None,'provider_response_verified':False,'credential_path':str(SECRET),'errors':[]}
key=None

def clean(s):
 s=str(s)
 if key:s=s.replace(key,'[REDACTED]')
 return re.sub(r'sk-or-[A-Za-z0-9_-]+','[REDACTED]',s)
def save(name,d):
 (O/name).write_text(clean(json.dumps(d,indent=2,ensure_ascii=False))+'\n')
def log(s):
 with (O/'submission.log').open('a') as f:f.write(now()+' '+clean(s)+'\n')
def finish(reason):
 meta['completed_at_utc']=now();meta['status']=reason
 save('submission_metadata.json',meta)
 if not meta['provider_response_verified']:
  (O/'review.md').write_text('# Claude review unavailable\n\nNo verified Claude review was obtained. Status: '+reason+'.\n\n'+ '\n'.join('- '+clean(x) for x in meta['errors'])+'\n\nThe scientific evidence is in package.md; request.json is sanitized and contains no Authorization header. See submission_metadata.json and submission.log for evidence.\n')
 log(reason)
 print(json.dumps({'status':reason,'submitted':meta['submitted'],'model':meta['model'],'http_status':meta['http_status'],'verified':meta['provider_response_verified']}))

# Parse only literal assignment values; never source/execute the credential file.
key=os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENROUTER_KEY')
if not key:
 try:
  for line in SECRET.read_text().splitlines():
   m=re.match(r'^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$',line)
   if m and 'OPENROUTER' in m[1].upper() and ('KEY' in m[1].upper() or 'TOKEN' in m[1].upper()):
    parts=shlex.split(m[2],comments=True)
    if len(parts)==1:key=parts[0];break
 except OSError as e:meta['errors'].append('Credential access failed: '+type(e).__name__+' at configured path')
if not key:meta['errors'].append('No usable OpenRouter credential available; authorized POST cannot be issued.')
if not key:
 save('response.json',{'local_failure':True,'provider_response_received':False,'errors':meta['errors']})
 finish('NOT_SUBMITTED_CREDENTIAL_ACCESS_DENIED');raise SystemExit(1)
# Model availability is verified live; no guessed model is claimed as offered.
models=[]
try:
 with open_retry('https://openrouter.ai/api/v1/models',timeout=20) as r:
  meta['models_http_status']=r.status; catalog=json.load(r)
 save('models.json',catalog)
 models=[m for m in catalog.get('data',[]) if m.get('id','').startswith('anthropic/') and any(t in m['id'].lower() for t in ('sonnet','opus'))]
 meta['offered_claude_models']=[m['id'] for m in models]
except Exception as e:meta['errors'].append('Model catalog unavailable: '+type(e).__name__+' '+clean(e))
if not key or not models:
 save('response.json',{'local_failure':True,'provider_response_received':False,'errors':meta['errors']})
 finish('NOT_SUBMITTED');raise SystemExit(1)
req=json.loads((O/'request.json').read_text())
# Conservative byte-based planning bound; actual provider token use is saved on response.
required=len(req['messages'][1]['content'].encode())//2+req['max_tokens']+2000
eligible=[m for m in models if m.get('context_length',0)>=required]
if not eligible:
 meta['errors'].append('No offered Claude Sonnet/Opus has sufficient conservative context budget for the intact package.')
 save('response.json',{'local_failure':True,'provider_response_received':False,'errors':meta['errors']});finish('NOT_SUBMITTED');raise SystemExit(1)
eligible=[m for m in eligible if m['id']=='anthropic/claude-sonnet-4.6']
if not eligible:
 meta['errors'].append('Requested exact Sonnet 4.6 model unavailable or insufficient context');save('response.json',{'local_failure':True,'errors':meta['errors']});finish('NOT_SUBMITTED');raise SystemExit(1)
preferred=['anthropic/claude-sonnet-4.6']
model=next((m for pid in preferred for m in eligible if m['id']==pid),eligible[0])
req['model']=model['id'];meta['model']=model['id'];meta['model_context_length']=model['context_length'];meta['conservative_context_budget']=required
save('request.json',req)
body=json.dumps(req,ensure_ascii=False).encode();meta['request_sha256']=hashlib.sha256(body).hexdigest();meta['request_bytes']=len(body)
log('Sending authorized HTTPS POST; model='+req['model'])
request=urllib.request.Request(URL,data=body,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','X-Title':'Opportunity Discrimination Scientific Peer Review'},method='POST')
try:
 meta['post_attempted_at_utc']=now()
 with open_retry(request,timeout=240) as r:
  meta['http_status']=r.status;raw=r.read().decode();meta['submitted']=True
 response=json.loads(raw);save('response.json',response)
 meta['response_model']=response.get('model');meta['provider']=response.get('provider');meta['response_id']=response.get('id');meta['usage']=response.get('usage')
 choices=response.get('choices',[]);choice=choices[0] if choices else {};content=choice.get('message',{}).get('content','');meta['finish_reason']=choice.get('finish_reason')
 actual=response.get('model','').lower()
 meta['claude_model_identity_verified']=actual=='anthropic/claude-sonnet-4.6'
 meta['review_characters']=len(content) if isinstance(content,str) else 0
 substantive=isinstance(content,str) and len(content)>5000 and all(t in content.lower() for t in ['calibration','reversal','iteration8','ablation','stop','pit'])
 meta['substantive_review_check']=substantive
 meta['completion_marker_verified']=isinstance(content,str) and 'END_OF_REVIEW' in content[-200:]
 substantive=substantive and meta['completion_marker_verified']
 meta['provider_response_verified']=meta['http_status']==200 and meta['claude_model_identity_verified'] and substantive and not response.get('error') and choice.get('finish_reason')=='stop'
 if meta['provider_response_verified']:
  (O/'review.md').write_text(clean(content)+'\n');finish('SUBMITTED_AND_VERIFIED')
 else:
  if isinstance(content,str):(O/'unverified_review.md').write_text(clean(content))
  meta['errors'].append('Response failed model identity, substantive content, or complete finish verification. Inspect response.json.');finish('RESPONSE_UNVERIFIED')
except urllib.error.HTTPError as e:
 meta['http_status']=e.code;meta['errors'].append('OpenRouter HTTP error '+str(e.code))
 save('response.json',{'http_status':e.code,'body':clean(e.read().decode(errors='replace'))});finish('PROVIDER_ERROR')
except Exception as e:
 meta['errors'].append('POST failed: '+type(e).__name__+' '+clean(e))
 save('response.json',{'local_failure':True,'provider_response_received':False,'errors':meta['errors']});finish('SUBMISSION_FAILED')
