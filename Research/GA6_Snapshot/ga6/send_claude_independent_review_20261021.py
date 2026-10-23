import os,json,urllib.request,urllib.error,time,hashlib,statistics
from pathlib import Path
root=Path('/opt/mts'); run=root/'ga6/runs'; source=run/'ga6_production_200_v1/all_evaluations.jsonl'
env=Path('/root/.openrouter_api_env')
line=next((x.strip() for x in env.read_text().splitlines() if 'OPENROUTER_API_KEY=' in x),None)
if not line:raise RuntimeError('OpenRouter credential missing')
key=line.split('=',1)[1].strip().strip('"').strip("'")
if not key:raise RuntimeError('OpenRouter credential empty')
rows=[json.loads(x) for x in source.open()]
summary=[]
for x in rows:
 r=x['result'];m=r['ga6_trade_metrics'];p=r.get('ga6_policy_oos') or {};v=p.get('validation') or {}
 summary.append({'g':x['generation'],'id':x['chromosome_id'][:12],'niche':x['genome']['niche'],'fitness':round(x['fitness'],3),'ev':m['net_ev'],'tail':m['worst_5pct_mean'],'win':m['win_rate'],'count':m['count'],'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'base_weight':x['genome']['base_weight'],'max_weight':x['genome']['max_weight'],'stop':x['genome']['stop_loss'],'exit_oos_delta':v.get('mean_incremental')})
files=['ga6/fitness.py','ga6/fitness_policy.py','ga6/guarded_evaluator_ga6.py','ga6/evaluator_adapter.py','ga6/portfolio_counterfactuals.py','ga6/GA6_RESEARCH_CONTRACT.md']
sources='\n\n'.join('FILE '+f+'\n'+(root/f).read_text() for f in files)
replay=(run/'controlled_capacity_replay_20261021.jsonl').read_text()
brief='''Perform an INDEPENDENT ADVERSARIAL audit of GA6. Do not defer to ChatGPT conclusions. Investigate paradigm failure and precise code-level defects. Distinguish shadow independent-unit-notional EV from realized cash-constrained portfolio CAGR/MDD. Why do fitness and EV rise while risk deteriorates? Investigate EV > 100%, trade-return accounting, gap and stop implementation, data leakage, survivorship, PIT, chronology, risk controls, portfolio sizing, selection biases, exit OOS validity, and scientific certification. Propose fundamentally different falsifiable experiments with priority, expected impact, and acceptance criteria. The 79/20/10/5 capacity replay barely changes 18.14% CAGR and 78% MDD. OmniFunds allegedly >50% return with 24% MDD, but raw OmniFunds files are NOT supplied, so do not claim verified comparability. Research only, DEV79; do not use blind sets. You are given ALL per-chromosome generation 1-8 summarized metrics (not raw trade histories), six actual source files, and controlled replay output. State clearly what you cannot establish without additional files.'''
payload={'model':'anthropic/claude-opus-4.6','messages':[{'role':'user','content':brief+'\n\nCODE:\n'+sources+'\n\nCAPACITY REPLAY:\n'+replay+'\n\nALL EVALUATIONS COMPACT METRICS:\n'+json.dumps(summary,separators=(',',':'))}],'max_tokens':9000,'temperature':0.2}
output=run/'claude_independent_review_20261021';output.mkdir(exist_ok=True)
(output/'submitted_manifest.json').write_text(json.dumps({'model':payload['model'],'evaluation_count':len(summary),'code_files':files,'payload_sha256':hashlib.sha256(json.dumps(payload).encode()).hexdigest(),'note':'API request includes summarized metrics, not full 2.36 MB archive'},indent=2))
request=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'MTS GA6 independent review'})
try:
 with urllib.request.urlopen(request,timeout=240) as response:
  raw=response.read().decode()
 (output/'raw_response.json').write_text(raw)
 obj=json.loads(raw)
 content=obj.get('choices',[{}])[0].get('message',{}).get('content','')
 (output/'claude_review.md').write_text(content if isinstance(content,str) else json.dumps(content,indent=2))
 print(json.dumps({'status':'SUCCESS','model':obj.get('model'),'usage':obj.get('usage'),'review_path':str(output/'claude_review.md'),'review_chars':len(content)}))
except urllib.error.HTTPError as e:
 body=e.read().decode(errors='replace')[:1800]
 (output/'api_error.txt').write_text('HTTP '+str(e.code)+' '+body)
 print(json.dumps({'status':'HTTP_ERROR','code':e.code,'message':body}))
except Exception as e:
 (output/'api_error.txt').write_text(type(e).__name__+': '+str(e))
 print(json.dumps({'status':'ERROR','type':type(e).__name__,'message':str(e)}))
