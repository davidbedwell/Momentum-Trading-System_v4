"""OpenRouter Claude raw-data Python tool loop. DRY RUN BY DEFAULT; --execute incurs API costs."""
import argparse,hashlib,json,pathlib,urllib.request
from ga6.claude_raw_python_tool import execute,DATA,FILES
ROOT=pathlib.Path('/opt/mts/ga6/runs/independent_review');MODEL='anthropic/claude-sonnet-4.6';MAX_TOKENS=16000
SYSTEM='You are an independent quantitative research auditor. You have a Python tool with read-only access to the complete GA6 raw parquet evidence. Explore the data yourself. Avoid relying on previous assistant conclusions. Explicitly distinguish descriptive associations from causal evidence, flag leakage, duplicate events, non-independent chromosomes, survivorship and retrospective tuning. Do not modify production code. Test multiple competing hypotheses. State evidence and limitations. Cite file names and calculations.'
TOOLS=[{'type':'function','function':{'name':'run_python','description':'Execute a Python analysis of the full read-only GA6 Parquet datasets. Python includes pandas, numpy, duckdb. Variable DATA is the directory containing the five parquet files. Execution has no network and runs under an unprivileged OS account. Print compact results; output is truncated.','parameters':{'type':'object','properties':{'code':{'type':'string','description':'Python code to run, using DATA / filename.parquet'}},'required':['code'],'additionalProperties':False}}}]
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--execute',action='store_true');ap.add_argument('--max-rounds',type=int,default=15);args=ap.parse_args()
 files={f:{'bytes':(ROOT/f).stat().st_size,'sha256':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in FILES}
 manifest={'model':MODEL,'max_tokens_per_response':MAX_TOKENS,'max_tool_rounds':args.max_rounds,'files':files,'tool':'run_python','dry_run':not args.execute}
 (ROOT/'CLAUDE_RAW_PYTHON_PREFLIGHT.json').write_text(json.dumps(manifest,indent=2))
 if not args.execute:print('PREFLIGHT_OK',json.dumps(manifest,indent=2));return
 key=next(x.split('=',1)[1].strip().strip('"').strip("'") for x in pathlib.Path('/root/.openrouter_api_env').read_text().splitlines() if x.startswith('OPENROUTER_API_KEY='))
 messages=[{'role':'system','content':SYSTEM},{'role':'user','content':'Independently audit GA6 full raw evidence. Files: '+', '.join(FILES)+'. Start by exploring schema, data integrity, and population. Run your own Python analyses before concluding. Produce a detailed, prioritized and falsifiable research report.'}];log=[]
 for round_no in range(args.max_rounds+1):
  payload={'model':MODEL,'messages':messages,'tools':TOOLS,'tool_choice':'auto','max_tokens':MAX_TOKENS,'temperature':0.2}
  req=urllib.request.Request('https://openrouter.ai/api/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json','HTTP-Referer':'https://chatgpt.com','X-Title':'GA6 Raw Python Independent Audit'})
  with urllib.request.urlopen(req,timeout=300) as response:result=json.load(response)
  choice=result['choices'][0];msg=choice['message'];messages.append(msg);log.append({'round':round_no,'finish_reason':choice.get('finish_reason'),'usage':result.get('usage'),'tool_calls':len(msg.get('tool_calls') or [])});print('ROUND',round_no,log[-1],flush=True)
  (ROOT/'CLAUDE_RAW_PYTHON_TRANSCRIPT.json').write_text(json.dumps({'messages':messages,'usage':log},indent=2))
  calls=msg.get('tool_calls') or []
  if not calls:
   (ROOT/'CLAUDE_RAW_PYTHON_REPORT.md').write_text(msg.get('content') or '');print('FINAL_REPORT_SAVED');return
  if round_no==args.max_rounds:print('ROUND_LIMIT_REACHED; transcript preserved');return
  for call in calls:
   if call['function']['name']!='run_python':answer={'error':'Unknown tool'}
   else:
    try:answer=execute(json.loads(call['function']['arguments'])['code'])
    except Exception as exc:answer={'error':str(exc)}
   messages.append({'role':'tool','tool_call_id':call['id'],'content':json.dumps(answer)})
if __name__=='__main__':main()
