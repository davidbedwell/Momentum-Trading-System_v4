import sys;sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import json,sqlite3,hashlib,statistics
from pathlib import Path
from ga5_redesign.canonical_engine import digest_file
root=Path('/opt/mts');p=root/'ga6/runs'
base=json.loads((p/'A_v2_matched_control_20261022/baseline_results.json').read_text())
d=root/'ga6/structural_independent_v2_20261022'
modules=('structural_runner_diagnostic.py','structural_batch.py','structural_candidate.py','structural_population.py','structural_portfolio_evaluator.py','structural_decision.py','family_logic.py','discovery_allocation.py','development_feedback_ledger.py')
code=hashlib.sha256(''.join(digest_file(d/n) for n in modules).encode()).hexdigest()
source=root/'ga5_redesign/exploratory79_ga4_enriched.parquet'
policy=root/'ga5_redesign/exploratory79_policy.json'
crash=root/'ga6/data/crash_defense_A_v2/STATE_TAPE_HISTORICAL.csv'
data_hash=digest_file(source)+'2019-01-01'+'2026-09-15'
policy_hash=digest_file(policy)+digest_file(crash)
db=sqlite3.connect(str(p/'A_v2_end_to_end_20261022/structural_evaluations.sqlite'))
rows=[]
for b in base:
 key=hashlib.sha256(f'{code}:{data_hash}:{policy_hash}:{b["identity"]}'.encode()).hexdigest()
 found=db.execute('select result from evaluations where key=?',(key,)).fetchone()
 if not found:raise RuntimeError('Missing matched revised result for '+b['identity'])
 r=json.loads(found[0])
 rows.append({'niche':b['niche'],'identity':b['identity'],'baseline_cagr':b['cagr'],'revised_cagr':r['cagr_diagnostic'],'delta_cagr_pp':100*(r['cagr_diagnostic']-b['cagr']),'baseline_mdd':b['mdd'],'revised_mdd':r['mdd_diagnostic'],'delta_mdd_pp':100*(r['mdd_diagnostic']-b['mdd']),'baseline_nav':b['final_nav'],'revised_nav':r['final_nav'],'baseline_trades':b['completed'],'revised_trades':r['ga6_completed_position_metrics']['completed_trades']})
out=p/'A_v2_matched_control_20261022/COMPARISON.json';out.write_text(json.dumps(rows,indent=2))
print('MATCHED',len(rows),'improved CAGR',sum(x['delta_cagr_pp']>0 for x in rows),'improved MDD',sum(x['delta_mdd_pp']>0 for x in rows))
print('MEAN DELTA CAGR pp',statistics.mean(x['delta_cagr_pp'] for x in rows),'MDD pp',statistics.mean(x['delta_mdd_pp'] for x in rows))
for x in sorted(rows,key=lambda x:x['revised_cagr'],reverse=True)[:8]:print(x['niche'], 'baseline',round(x['baseline_cagr']*100,2),round(x['baseline_mdd']*100,2),'revised',round(x['revised_cagr']*100,2),round(x['revised_mdd']*100,2),'delta',round(x['delta_cagr_pp'],2),round(x['delta_mdd_pp'],2))
print('SAVED',out)
