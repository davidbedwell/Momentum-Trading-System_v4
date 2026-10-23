import json,hashlib,datetime,urllib.request,urllib.error,os
from pathlib import Path
root=Path('/opt/mts/ga6_h')
out=root/'witness_review'/'grok_chromosome_review_20261022'
out.mkdir(parents=True,exist_ok=True)
paths=['GA6H_CHROMOSOME_SPEC_V02_20261022.md','DESIGN_v0_1.md','UNIVERSE_REQUIREMENTS_v0_2.md','context_free_genome.py','genetic_operators.py','context_scoring.py','discovery_fitness.py','evolution_engine.py','quarterly_embargo.py','portfolio_execution.py','daily_simulator.py']
parts=[]
for p in paths:
    source=(root/p).read_text()
    parts.append('===== '+p+' =====\n'+source[:24000])
instruction="""You are Claude, independent adversarial quantitative research engineer. Audit the COMPLETE GA6-H chromosome design and implemented source below. Focus specifically on:
(1) chromosome grammar and nested tree validity/crossover/mutation;
(2) discovery-only fitness (net EV, EV per session, statistical reliability, in-training consistency, actual opportunity coverage), NOT CAGR/MDD during breeding;
(3) Pareto selection, archive epsilon cell and 100-generation stagnation reset, with code-level failure modes;
(4) data leakage safeguards, close-t to next-open execution, adjusted/unadjusted prices, earnings timing, PIT universe, survivorship and missing data;
(5) strict discovery vs transport OOS vs sealed blind separation. Do NOT use OOS to guide breeding.
(6) scientific search coverage and runtime engineering.
ABSOLUTE PRIORITY: User does NOT want a days/weeks-long study or bloated framework. Propose the minimum scientifically defensible improvements enabling a rapid working GA6-H evolutionary experiment on existing server/data. Classify EACH proposal as MUST-FIX BEFORE FIRST EXPERIMENT / LOW-COST HIGH-VALUE / DEFER UNTIL CERTIFICATION / REJECT AS OVERENGINEERING. Give rough coding effort and CPU/runtime impact. Explicitly identify anything that can be removed or deferred, and 3-5 fastest path steps. Avoid requiring expensive new datasets or a full 503-stock PIT reconstruction before exploratory diagnostic research; disclose limitations. Never claim current synthetic fitness is actual EV. 1-40 sessions strict; preserve GA6 running independently. Challenge assumptions, don't agree reflexively. Be precise about source-level evidence, not speculative bugs. Limit response to ~2200 words."""
evaluation = '''INDEPENDENT CHATGPT EVALUATION OF CLAUDE:
Agree: A real historical, price-based evaluator is mandatory before interpreting GA discoveries; preserve nested tree crossover; guard discovery data; retain archive genomes; distinguish exploration from certification; avoid weeks of PIT reconstruction at this stage.
Disagree/qualify: Claude's proposed rank-IC evaluator cannot be called net trade EV, and mapping IC directly to net_ev is scientifically invalid. Use executable signals, next-session open entry, 1-40-session exits, realized costs, stops, and observed net P&L to compute net EV and EV/session. IC may be auxiliary diagnostic only. Claude's suggested 20-day labels ignore variable holding-period chromosomes and path-dependent exits. Top-minus-bottom spreads are not executable long-only trade EV. EPS should be empirically calibrated on discovery data, not asserted as universal constants. Stagnation behavior should follow an explicit bounded compute budget; indefinite reset-and-continue contradicts the user's efficiency priority. Reset only with a bounded restart count, or stop after plateau and report it. The duplicate-fitness Pareto crash claim needs a reproducer, not speculative acceptance. A price adjustment flag is not verification. Do not confuse calendar-date separation with true out-of-sample stock transport; enforce both as appropriate without touching sealed blinds.
Priority: smallest real price-based evaluator with cached features, 1-40 sessions, proper execution/cost accounting, basic anti-leakage checks, and bounded CPU budget. Preserve full grammar/capabilities, do not simplify away chromosome functionality. Validate bug claims with tests before changing code.
'''
instruction = '''You are Grok, an INDEPENDENT adversarial quantitative software reviewer. The package includes the entire GA6-H chromosome specification and implementation, Claude's complete review, and ChatGPT's independent evaluation. Challenge ALL THREE, especially the fitness semantics (IC vs executable net EV), grammar/operators, Pareto selection, stagnation/restarts, leakage, discovery vs OOS vs sealed blind, runtime efficiency, and the 1-40-session swing-trading objective. Identify actual code-backed bugs vs speculation. Classify each proposal MUST BEFORE REAL DISCOVERY / QUICK WIN / DEFER CERTIFICATION / REJECT. User explicitly requires a fast experiment, not days/weeks of engineering; preserve evaluator capabilities and avoid unnecessary complexity. Propose a minimum viable scientific implementation, bounded CPU budget, and prioritized fixes. State disagreements with Claude and ChatGPT. Do not assert synthetic metrics are trade EV.'''
message=instruction+'\n\n'+'\n\n'.join(parts)+'\n\n===== CLAUDE COMPLETE REVIEW =====\n'+(root/'witness_review'/'chromosome_design_20261022'/'CLAUDE_CHROMOSOME_AUDIT.md').read_text()+'\n\n===== CHATGPT EVALUATION =====\n'+evaluation
keyline=next((x.strip() for x in Path('/root/.openrouter_api_env').read_text().splitlines() if 'OPENROUTER_API_KEY=' in x),None)
if not keyline:raise RuntimeError('OpenRouter credential missing')
key=keyline.split('=',1)[1].strip().strip('"').strip("'")
payload={'model':'x-ai/grok-4.5','messages':[{'role':'user','content':message}],'max_tokens':7500,'temperature':0.1}
data=json.dumps(payload).encode()
meta={'requested_model':payload['model'],'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'request_sha256':hashlib.sha256(data).hexdigest(),'files':paths,'characters':len(message)}
(out/'submission_manifest.json').write_text(json.dumps(meta,indent=2))
req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=data,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'GA6-H Grok independent audit'})
try:
    with urllib.request.urlopen(req,timeout=240) as response:result=json.load(response)
    (out/'raw_response.json').write_text(json.dumps(result,indent=2))
    answer=result.get('choices',[{}])[0].get('message',{}).get('content','')
    (out/'GROK_CHROMOSOME_AUDIT.md').write_text(answer if isinstance(answer,str) else json.dumps(answer,indent=2))
    print(json.dumps({'status':'SUCCESS','model':result.get('model'),'chars':len(answer),'usage':result.get('usage'),'path':str(out/'GROK_CHROMOSOME_AUDIT.md')}))
except Exception as e:
    (out/'error.txt').write_text(type(e).__name__+': '+str(e))
    print(json.dumps({'status':'ERROR','error':str(e)[:300]}))
