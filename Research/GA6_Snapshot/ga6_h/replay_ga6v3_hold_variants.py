import json,sqlite3,hashlib
from pathlib import Path
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
root=Path('/opt/mts')
run=root/'ga6/runs/A_v2_full_evolution_20261022'
identity='0f56bbba4dc2fc7ac656da8c74fefa32d64a3e747355e55944829df05778eee2'
conn=sqlite3.connect('file:'+str(run/'structural_manifest.sqlite')+'?mode=ro',uri=True)
record=conn.execute('select definition_json,digest from candidates where structural_id=?',(identity,)).fetchone()
assert record and hashlib.sha256(record[0].encode()).hexdigest()==record[1]
candidate=StructuralCandidate.restore(json.loads(record[0]))
source=root/'ga5_redesign/exploratory79_ga4_enriched.parquet'
frame=pd.read_parquet(source)
frame=frame[(frame.date>='2019-01-01')&(frame.date<'2025-01-01')]
prepared=PreparedSessions(frame)
policy_json=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
state=build_revised_daily_state().set_index('date')
state.index=state.index.strftime('%Y-%m-%d')
risk_veto={d:v for d,v in policy_json['risk_veto'].items() if d in prepared.dates}
for day in sorted(prepared.dates):
 idx=state.index.get_loc(day)
 assert idx>0
 risk_veto[day]=bool(risk_veto[day] is True and not state.iloc[idx-1].defensive)
policy={'blocked':{t:frozenset(v) for t,v in policy_json['blocked'].items()},'membership':{(d,t):v for d,t,v in policy_json['membership'] if d in prepared.dates},'risk_veto':risk_veto,'annual_cash_yield':policy_json['cash_proxy_annual_yield']}
print('REPLAY_INPUTS',len(prepared.dates),identity,flush=True)
output=[]
for hold in (40,35,30,25,20,15,10):
 result=evaluate(prepared,candidate.genome,entry_tree=candidate.entry_tree,max_swing_sessions=hold,**policy)
 record={'hold':hold,'cagr':result['cagr_diagnostic'],'mdd':result['mdd_diagnostic'],'final_nav':result['final_nav'],'trades':result['ga6_completed_position_metrics']['completed_trades'],'avg_sessions':result['ga6_completed_position_metrics']['avg_sessions'],'fees':result['reconciliation']['fees']}
 output.append(record)
 print('VARIANT',json.dumps(record),flush=True)
 if hold==40:
  assert abs(record['cagr']-0.46612518936207237)<1e-9,'BASELINE_CAGR_MISMATCH'
  assert abs(record['mdd']+0.154352878015385)<1e-9,'BASELINE_MDD_MISMATCH'
(root/'ga6_h/audits/ga6v3_hold_variants_20261023.json').write_text(json.dumps({'chromosome':identity,'variants':output},indent=2))
print('REPLAY_PASS',flush=True)
