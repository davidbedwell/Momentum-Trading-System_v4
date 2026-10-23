import sqlite3,json,hashlib
from pathlib import Path
from ga5_redesign.canonical_engine import digest_file
r=Path('/opt/mts')
p=r/'ga6/runs/A_v2_full_evolution_20261022'
m=r/'ga6/structural_independent_v2_20261022'
modules=('structural_runner_A_v2.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
code=hashlib.sha256(''.join(digest_file(m/n) for n in modules).encode()).hexdigest()
data=digest_file(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')+'2019-01-01'+'2025-01-01'
policy=digest_file(r/'ga5_redesign/exploratory79_policy.json')+digest_file(r/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')
c=sqlite3.connect('file:'+str(p/'structural_manifest.sqlite')+'?mode=ro',uri=True)
target='c815bfda0dd8318e0fc377eaad576578bb36e715014baf8bab19a0a61c8c3f8c'
for identity,definition in c.execute('select structural_id,definition_json from candidates'):
 key=hashlib.sha256(f'{code}:{data}:{policy}:{identity}'.encode()).hexdigest()
 if key==target:
  print('FOUND',identity,definition,flush=True)
  break
else:print('NOT_FOUND',len(list(c.execute('select structural_id from candidates'))),code,flush=True)
