"""Read-only evidence assembly; no experiment imports or replays."""
from pathlib import Path
import json,hashlib,gzip,collections,shutil
O=Path(__file__).resolve().parent; B=O.parent
manifest=[]; sections=[]
def register(p,mode):
 raw=p.read_bytes(); entry={'path':str(p.relative_to(B)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'representation':mode};manifest.append(entry)
 dest=O/'evidence'/p.relative_to(B);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest)
 return raw

def section(p,content,mode):
 register(p,mode);sections.append('\n## '+str(p.relative_to(B))+'\n\n'+content+'\n')
questions='''# Iteration5/6 scientific evidence and architectural design request

All data here are SYNTHETIC, from the explicitly supplied DGP; no real alpha, production readiness, or real PIT provenance is established. All final seeds have now been viewed. This is an external DESIGN request, not implementation authorization. Do not merely audit statistics. Provide a SPECIFIC actionable ALTERNATIVE ARCHITECTURE, equations and online pseudocode grounded in the supplied source and evidence. Distinguish measured facts, assumptions, theoretical limits, and proposed hypotheses. Treat the original Claude review as historical advice, not authority.

Answer all requirements:
1. Mathematically identifiable earliest reversal detection using ONLY PIT observables. Define filtration and signal+3 outcome availability, prove or qualify observational equivalence before eligible outcomes; distinguish the hard 3-session limit from statistical accumulation delay. Propose concrete online sequential algorithms (e.g. likelihood ratio/CUSUM/mixture e-process), statistic, windows or horizon-free scheme, numerical thresholds, multiplicity and false-alarm correction across assets/cells/channels/time, false-alarm assumptions, and detection-delay/power calculation under this exact DGP. Address estimated baseline uncertainty and missing extreme-cell dates. Compare against current 2/4/8-window gate. Avoid oracle switch times and latent truth.
2. Eliminate more false GREAT without lowering stable return: distinguish a finite-sample observation from a population guarantee; assess whether both demands are mathematically achievable. Account explicitly for unavoidable 3-session exposure, funding, costs, liquidation and delayed outcomes. Design exposure/risk decision policy, any abstention/recovery logic, and constrained objective. Give a tradeoff frontier and refuse impossible zero-cost guarantees. No synthetic informative indicator may be silently invented.
3. Restore missing AVERAGE without forced labels, widened economic bands, or tuning these held-out tapes. Explain estimand (individual latent vs conditional mean vs realized return), center-to-boundary margin and uncertainty. Give a TRAINING-ONLY identifiable design, independent-date/sample-size calculation, feature/model changes if actually justified, calibration split, uncertainty validity, and conditions under which class support is impossible or uncertifiable. No guarantee of all classes on every random tape unless proved.
4. Provide a concrete ALTERNATIVE ARCHITECTURE with exact available inputs; equations/pseudocode for fitting, calibration, prediction, monitoring, portfolio policy and recovery; explicit training-only choices versus independent calibration; prioritized modifications with source function targets; expected benefits and costs as hypotheses; new external commitment and untouched validation plan with episode/seed denominators, multiple testing correction, stable return noninferiority and false-GREAT/detection-delay metrics. State falsification and stop criteria with numerical candidate thresholds and explain which require stakeholder risk choices. Separate impossible from engineering-fixable. Critique DGP overfitting, reviewed-holdout adaptation and model complexity; no claims of real alpha. Include minimum new data needed for each claim.

Package integrity: complete Python sources, README, preregistration, commitments, tests and archived test output, CSV metrics/confusion/detection/portfolio/audits are transmitted verbatim. Reports use semantic compaction: discrimination rows retain all fields EXCEPT train_dates/cal_dates lists, which are represented by count, endpoints, contiguity, SHA256 of canonical JSON; repetitive daily channel traces retain counts, hash, first four/last two rows and alarm neighborhoods; full reports are archived locally with original SHA256. Representative ledger examples are deterministic samples, NOT full-ledger statistical evidence; exact whole-ledger denominators are supplied. No portfolios or tests are rerun. Original review and original review metadata are included. All hashes are local provenance, not trusted timestamps.
'''
section(B/'claude_external_review/review.md',(B/'claude_external_review/review.md').read_text(),'verbatim historical Claude review')
section(B/'claude_external_review/submission_metadata.json',(B/'claude_external_review/submission_metadata.json').read_text(),'verbatim historical submission metadata')
def compact(v):
 if isinstance(v,dict) and 'trace' in v:
  trace=v['trace']; event_indices={e['index'] for e in v.get('events',[])}
  return {**{k:compact(x) for k,x in v.items() if k!='trace'},'trace_summary':{'rows':len(trace),'canonical_json_sha256':hashlib.sha256(json.dumps(trace,separators=(',',':')).encode()).hexdigest(),'alarm_rows':sum(bool(x.get('alarm')) for x in trace),'selected_rows':[r for j,r in enumerate(trace) if j<4 or j>=len(trace)-2 or any(abs(r['index']-i)<=1 for i in event_indices)]}}
 if isinstance(v,dict):
  return {k:({'count':len(x),'first':x[0] if x else None,'last':x[-1] if x else None,'contiguous':all(b==a+1 for a,b in zip(x,x[1:])),'canonical_json_sha256':hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()} if k in ('train_dates','cal_dates') and isinstance(x,list) else compact(x)) for k,x in v.items()}
 if isinstance(v,list):return [compact(x) for x in v]
 return v
for n in (5,6):
 p=B/f'discrimination_iteration{n}'
 for f in sorted(p.iterdir()):
  if f.is_file() and f.suffix in ('.py','.md','.csv','.log','.json'):
   if f.name in ('report.json','raw_report.json'):
    if f.name=='raw_report.json':register(f,'archived only; pre-correction duplicate, final report transmitted');continue
    section(f,'```json\n'+json.dumps(compact(json.loads(f.read_text())),separators=(',',':'))+'\n```','semantic compaction; only date index arrays summarized')
   else:section(f,'```\n'+f.read_text()+'\n```','verbatim')
 for fn in ('opportunities.jsonl.gz','replays.jsonl.gz','corrected_benchmark_replays.jsonl.gz'):
  f=p/fn
  if not f.exists():continue
  register(f,'archived full compressed ledger; exact counts and deterministic representative excerpts transmitted')
  groups=collections.defaultdict(lambda:{'rows':0,'funded_opportunities':0,'trades':0,'daily_rows':0}); samples={}
  with gzip.open(f,'rt') as stream:
   for rowno,line in enumerate(stream,1):
    z=json.loads(line);g=str((z.get('phase'),z.get('seed'),z.get('scenario'),z.get('variant')));a=groups[g];a['rows']+=1
    if 'trades' in z:
     a['trades']+=len(z['trades']);a['daily_rows']+=len(z.get('daily',[]))
     if g not in samples:
      samples[g]={'source_line':rowno,'metadata':{k:v for k,v in z.items() if k not in ('trades','daily')},'trades_first_2':z['trades'][:2],'trades_last_1':z['trades'][-1:],'daily_first_1':z.get('daily',[])[:1],'daily_last_1':z.get('daily',[])[-1:]}
    else:
     a['funded_opportunities']+=bool(z.get('funded'));idx=z.get('index',-1);label=z.get('label',z.get('inferred_tier'));truth=z.get('truth',z.get('true_ev'))
     category='false_GREAT' if label=='GREAT' and truth==-.012 else 'AVERAGE' if label=='AVERAGE' else 'funded' if z.get('funded') else 'other'
     key=g+'|'+category
     if key not in samples:samples[key]={'source_line':rowno,'row':z}
  sections.append('\n## '+str(f.relative_to(B))+' exact ledger counts and samples\n```json\n'+json.dumps({'group_counts':dict(groups),'samples':samples},separators=(',',':'))+'\n```')
# Frozen baseline comparator used by iteration5; include all local Python dependencies from iteration2.
for f in sorted((B/'discrimination_iteration2').glob('*.py')):section(f,'```python\n'+f.read_text()+'\n```','verbatim baseline reference source')
for rel in ['opportunity_evaluator_fix/experiment.py','scaling_blocker_audit/audit.py']:
 f=B/rel
 if f.exists():section(f,'```python\n'+f.read_text()+'\n```','verbatim inherited reference dependency; ancillary legacy production imports are not replayed')
package=questions+'\n'.join(sections)
(O/'package.md').write_text(package)
(O/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
req={'model':'anthropic/claude-sonnet-4.6','temperature':0.2,'max_tokens':22000,'messages':[{'role':'system','content':'You are a rigorous scientific statistician and online decision-systems architect. Supply an actionable alternative architecture, not just an audit. Use only supplied evidence; do not pretend to execute code. Separate impossibility results from engineering fixes and assumptions from guarantees. No real alpha claims.'},{'role':'user','content':package}]}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'package_bytes':len(package.encode()),'manifest_files':len(manifest)}))
