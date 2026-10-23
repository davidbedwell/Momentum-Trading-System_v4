import json,hashlib,datetime,urllib.request,urllib.error
from pathlib import Path
root=Path('/opt/mts/ga6_h'); out=root/'witness_review';out.mkdir(exist_ok=True)
plan=(root/'GA4_TO_GA6_AUDIT_GA6H_PLAN_WITNESS_20261022.md').read_text()
evidence=[]
for path in ['/opt/mts/ga6/GA5_GA6_SCOPE_AUDIT.md','/opt/mts/ga6/GA6_RESEARCH_CONTRACT.md','/opt/mts/ga6/runs/post_v3_comparison_20261022/comparison_report.json','/opt/mts/ga6/runs/GA6_DUAL_TRACK_REDESIGN_20261021/quick_cross_comparison.json','/opt/mts/ga6_h/audits/ranking_baseline_v1.json']:
    p=Path(path);evidence.append('SOURCE: '+path+'\n'+p.read_text()[:15000])
rows=json.loads(Path('/opt/mts/ga6/runs/A_v2_matched_control_20261022/COMPARISON.json').read_text())
summary={'n':len(rows),'both_better':sum(x['delta_cagr_pp']>0 and x['delta_mdd_pp']>0 for x in rows),'cagr_better':sum(x['delta_cagr_pp']>0 for x in rows),'cagr_worse':sum(x['delta_cagr_pp']<0 for x in rows),'mdd_better':sum(x['delta_mdd_pp']>0 for x in rows),'rows':rows}
message='INDEPENDENT ADVERSARIAL SECOND-WITNESS REVIEW. Do not defer to the first author. Review the attached plan and actual evidence. Identify unsupported claims, false GA4-to-GA6 causal attribution, future leakage, invalid selection and missing engineering gates. Produce a prioritized defect table with severity, exact evidence, tests and fixes; evaluate GA6-H design without inheriting GA6 niches. Separate PROVEN, PLAUSIBLE, UNPROVEN. Do not invent source files or performance. Return a concrete revised acceptance checklist.\n\nPLAN:\n'+plan+'\n\nEVIDENCE:\n'+'\n\n'.join(evidence)+'\nMATCHED_COMPARISON:\n'+json.dumps(summary)
keyline=next((x.strip() for x in Path('/root/.openrouter_api_env').read_text().splitlines() if 'OPENROUTER_API_KEY=' in x),None)
if not keyline:raise RuntimeError('OpenRouter credential missing')
key=keyline.split('=',1)[1].strip().strip('"').strip("'")
payload={'model':'anthropic/claude-sonnet-4.6','messages':[{'role':'user','content':message}],'max_tokens':6500,'temperature':0.1}
data=json.dumps(payload).encode()
meta={'model_requested':payload['model'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'sha256':hashlib.sha256(data).hexdigest(),'plan_sha256':hashlib.sha256(plan.encode()).hexdigest(),'evidence_sources':5,'matched_rows':len(rows)}
(out/'submission_manifest.json').write_text(json.dumps(meta,indent=2))
req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=data,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'GA6-H second witness'})
try:
    with urllib.request.urlopen(req,timeout=240) as resp: result=json.load(resp)
    (out/'raw_response.json').write_text(json.dumps(result,indent=2))
    ans=result.get('choices',[{}])[0].get('message',{}).get('content','')
    (out/'CLAUDE_WITNESS_REVIEW.md').write_text(ans if isinstance(ans,str) else json.dumps(ans,indent=2))
    print(json.dumps({'status':'SUCCESS','model':result.get('model'),'response_chars':len(ans),'review_path':str(out/'CLAUDE_WITNESS_REVIEW.md'),'usage':result.get('usage')}))
except Exception as e:
    (out/'error.txt').write_text(type(e).__name__+': '+str(e))
    print(json.dumps({'status':'ERROR','type':type(e).__name__,'message':str(e)[:400]}))
