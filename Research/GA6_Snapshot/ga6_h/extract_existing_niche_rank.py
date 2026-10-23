import json,sqlite3,hashlib
from pathlib import Path
from ga5_redesign.canonical_engine import digest_file
root=Path('/opt/mts');run=root/'ga6/runs/A_v2_full_evolution_20261022'
checkpoint=json.loads((run/'structural_checkpoint.json').read_text())
members=checkpoint['members']
print('CHECKPOINT',checkpoint['generation'],'members',len(members),'niches',len(set(x['genome']['niche'] for x in members)),flush=True)
m=root/'ga6/structural_independent_v2_20261022'
modules=('structural_runner_A_v2.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
code=hashlib.sha256(''.join(digest_file(m/n) for n in modules).encode()).hexdigest()
data=digest_file(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')+'2019-01-01'+'2025-01-01'
policy=digest_file(root/'ga5_redesign/exploratory79_policy.json')+digest_file(root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')
db=sqlite3.connect('file:'+str(run/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
ranked=[]
for member in members:
 identity=member['structural_id']
 key=hashlib.sha256(f'{code}:{data}:{policy}:{identity}'.encode()).hexdigest()
 row=db.execute('select result from evaluations where key=?',(key,)).fetchone()
 if row:
  r=json.loads(row[0]);ranked.append({'identity':identity,'niche':member['genome']['niche'],'cagr':r.get('cagr_diagnostic'),'mdd':r.get('mdd_diagnostic'),'trades':r.get('ga6_completed_position_metrics',{}).get('completed_trades')})
print('MATCHED',len(ranked),flush=True)
best={}
for r in ranked:
 if r['cagr'] is not None and (r['niche'] not in best or r['cagr']>best[r['niche']]['cagr']):best[r['niche']]=r
rows=sorted(best.values(),key=lambda x:-x['cagr'])
print('NICHE_LEADERS',json.dumps(rows),flush=True)
out=root/'ga6_h/audits/ga6v3_existing_niche_leaders_20261023.json'
out.write_text(json.dumps({'source':'original final generation checkpoint','generation':checkpoint['generation'],'distinct_by':'original protected niche','leaders':rows},indent=2))
print('OUTPUT',out,flush=True)
