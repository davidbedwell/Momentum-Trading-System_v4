import json,hashlib,sqlite3
from pathlib import Path
import pandas as pd
from ga5_redesign.canonical_engine import digest_file
r=Path('/opt/mts');run=r/'ga6/runs/A_v2_full_evolution_20261022'
d=pd.read_csv(r/'ga6_h/audits/ga6v3_400_DEV87_20261023.csv')
m=r/'ga6/structural_independent_v2_20261022'
mods=('structural_runner_A_v2.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
code=hashlib.sha256(''.join(digest_file(m/n) for n in mods).encode()).hexdigest()
data=digest_file(r/'ga5_redesign/exploratory79_ga4_enriched.parquet')+'2019-01-01'+'2025-01-01'
policy=digest_file(r/'ga5_redesign/exploratory79_policy.json')+digest_file(r/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv')
db=sqlite3.connect('file:'+str(run/'structural_evaluations.sqlite')+'?mode=ro',uri=True)
rows=[]
for x in d.itertuples():
 key=hashlib.sha256(f'{code}:{data}:{policy}:{x.identity}'.encode()).hexdigest()
 z=db.execute('select result from evaluations where key=?',(key,)).fetchone()
 if z:
  a=json.loads(z[0])
  rows.append(dict(identity=x.identity,niche=x.niche,dev_cagr=a['cagr_diagnostic'],dev_mdd=a['mdd_diagnostic'],dev_trades=a['ga6_completed_position_metrics']['completed_trades'],hold_cagr=x.cagr,hold_mdd=x.mdd,hold_trades=x.trades,delta_cagr=x.cagr-a['cagr_diagnostic']))
p=pd.DataFrame(rows)
out=r/'ga6_h/audits/ga6v3_DEV87_vs_development_20261023.csv';p.to_csv(out,index=False)
print('MATCHED',len(p),'OF',len(d))
print('PAIRED',p[['dev_cagr','hold_cagr','delta_cagr','dev_mdd','hold_mdd','dev_trades','hold_trades']].describe().round(4).to_string())
print('NICHES',p.groupby('niche')[['dev_cagr','hold_cagr','delta_cagr','dev_trades','hold_trades']].median().round(4).to_string())
print('IMPROVED',sum(p.delta_cagr>0),'WORSENED',sum(p.delta_cagr<0))
print('SAVED',out)
