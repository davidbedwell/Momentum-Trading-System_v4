import json,sqlite3,hashlib,statistics
from pathlib import Path
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
from ga5_redesign.canonical_engine import digest_file
root=Path('/opt/mts');run=root/'ga6/runs/A_v2_full_evolution_20261022'
db=sqlite3.connect('file:'+str(run/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
top=db.execute("select key,json_extract(result,'$.cagr_diagnostic'),json_extract(result,'$.mdd_diagnostic') from evaluations where json_extract(result,'$.ga6_completed_position_metrics.completed_trades')>=30 order by json_extract(result,'$.cagr_diagnostic') desc limit 10").fetchall()
print('TOP10',json.dumps(top),flush=True)
m=root/'ga6/structural_independent_v2_20261022'
modules=('structural_runner_A_v2.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
code=hashlib.sha256(''.join(digest_file(m/n) for n in modules).encode()).hexdigest()
data=digest_file(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')+'2019-01-01'+'2025-01-01'
policy_hash=digest_file(root/'ga5_redesign/exploratory79_policy.json')+digest_file(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')
manifest=sqlite3.connect('file:'+str(run/'structural_manifest.sqlite')+'?mode=ro',uri=True)
wanted={x[0] for x in top};found={}
for identity,definition,digest in manifest.execute('select structural_id,definition_json,digest from candidates'):
 key=hashlib.sha256(f'{code}:{data}:{policy_hash}:{identity}'.encode()).hexdigest()
 if key in wanted:
  assert hashlib.sha256(definition.encode()).hexdigest()==digest
  found[key]=StructuralCandidate.restore(json.loads(definition))
assert len(found)==len(top),(len(found),len(top))
frame=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2019-01-01')&(frame.date<'2025-01-01')]
prepared=PreparedSessions(frame)
j=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
state=build_revised_daily_state().set_index('date');state.index=state.index.strftime('%Y-%m-%d')
veto={d:v for d,v in j['risk_veto'].items() if d in prepared.dates}
for d in prepared.dates:
 i=state.index.get_loc(d);assert i>0
 veto[d]=bool(veto[d] is True and not state.iloc[i-1].defensive)
policy={'blocked':{t:frozenset(v) for t,v in j['blocked'].items()},'membership':{(d,t):v for d,t,v in j['membership'] if d in prepared.dates},'risk_veto':veto,'annual_cash_yield':j['cash_proxy_annual_yield']}
results=[]
for rank,(key,cagr,mdd) in enumerate(top,1):
 candidate=found[key]
 r=evaluate(prepared,candidate.genome,entry_tree=candidate.entry_tree,max_swing_sessions=40,allocation_audit=True,**policy)
 assert abs(r['cagr_diagnostic']-cagr)<1e-9 and abs(r['mdd_diagnostic']-mdd)<1e-9
 a=r['allocation_audit'];trades=a['completed'];pm=r['ga6_completed_position_metrics']
 assert len(trades)==pm['completed_trades']
 item={'rank':rank,'identity':candidate.identity(),'niche':candidate.genome.niche,'cagr':cagr,'mdd':mdd,'trades':len(trades),'win_rate':pm['win_rate'],'avg_hold':pm['avg_sessions'],'base_weight':candidate.genome.base_weight,'max_weight':candidate.genome.max_weight,'risk_budget':candidate.genome.risk_budget,'avg_initial_weight':statistics.mean(t['entry_weight'] for t in trades),'max_peak_weight':max(t['peak_weight'] for t in trades),'scale_ins':sum(t['scaleins'] for t in trades),'positions_scaled':sum(t['scaleins']>0 for t in trades),'over20':sum(t['peak_weight']>.20 for t in trades),'over30':sum(t['peak_weight']>.30 for t in trades),'over50':sum(t['peak_weight']>.50 for t in trades),'top_positions':sorted(trades,key=lambda t:t['peak_weight'],reverse=True)[:5]}
 results.append(item)
 print('RESULT',json.dumps(item),flush=True)
out=root/'ga6_h/audits/ga6v3_top10_allocation_audit_20261023.json'
out.write_text(json.dumps({'ranking':'highest CAGR among stored evaluations with at least 30 completed positions','period':'2019-01-02 to 2024-12-31','results':results},indent=2))
print('DONE',out,flush=True)
