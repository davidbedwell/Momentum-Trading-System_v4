import json,sqlite3,hashlib
from pathlib import Path
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga6.crash_defense_A_v2_adapter import build_revised_daily_state
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from ga6_h.hold_variant_evaluator import evaluate
root=Path('/opt/mts')
identity='0f56bbba4dc2fc7ac656da8c74fefa32d64a3e747355e55944829df05778eee2'
p=root/'ga6/runs/A_v2_full_evolution_20261022/structural_manifest.sqlite'
c=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
definition,digest=c.execute('select definition_json,digest from candidates where structural_id=?',(identity,)).fetchone()
assert hashlib.sha256(definition.encode()).hexdigest()==digest
candidate=StructuralCandidate.restore(json.loads(definition))
frame=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
frame=frame[(frame.date>='2019-01-01')&(frame.date<'2025-01-01')]
prepared=PreparedSessions(frame)
j=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
state=build_revised_daily_state().set_index('date')
state.index=state.index.strftime('%Y-%m-%d')
veto={d:v for d,v in j['risk_veto'].items() if d in prepared.dates}
for d in prepared.dates:
 i=state.index.get_loc(d)
 assert i>0
 veto[d]=bool(veto[d] is True and not state.iloc[i-1].defensive)
r=evaluate(prepared,candidate.genome,entry_tree=candidate.entry_tree,max_swing_sessions=40,allocation_audit=True,blocked={t:frozenset(v) for t,v in j['blocked'].items()},membership={(d,t):v for d,t,v in j['membership'] if d in prepared.dates},risk_veto=veto,annual_cash_yield=j['cash_proxy_annual_yield'])
assert abs(r['cagr_diagnostic']-.46612518936207237)<1e-9
assert abs(r['mdd_diagnostic']+.154352878015385)<1e-9
a=r['allocation_audit']
assert len(a['completed'])==r['ga6_completed_position_metrics']['completed_trades']
out=root/'ga6_h/audits/ga6v3_allocation_audit_20261023.json'
out.write_text(json.dumps({'identity':identity,'cagr':r['cagr_diagnostic'],'mdd':r['mdd_diagnostic'],'allocation':a},indent=2))
trades=a['completed']
print('COUNT',len(trades),'FILL_COUNT',len(a['fills']),'SCALE_INS',sum(t['scaleins'] for t in trades),flush=True)
for threshold in (.03,.10,.20,.30,.40,.50,.60,.69):
 print('PEAK_GT',threshold,sum(t['peak_weight']>threshold for t in trades),flush=True)
print('TOP',json.dumps(sorted(trades,key=lambda t:t['peak_weight'],reverse=True)[:12]),flush=True)
print('ENTRY_STATS',json.dumps({'min':min(t['entry_weight'] for t in trades),'max':max(t['entry_weight'] for t in trades),'mean':sum(t['entry_weight'] for t in trades)/len(trades)}),flush=True)
print('OUTPUT',out,flush=True)
