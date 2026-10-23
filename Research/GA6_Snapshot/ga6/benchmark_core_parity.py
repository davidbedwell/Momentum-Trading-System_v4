import sys,json,time,math
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
from ga6.guarded_evaluator_ga6 import evaluate as old
from ga6.guarded_evaluator_ga6_optimized_candidate import evaluate as new
root=Path('/opt/mts/ga5_redesign');f=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');f=f[(f.date>='2005-09-14')&(f.date<'2026-09-15')];prepared=PreparedSessions(f)
p=json.loads((root/'exploratory79_policy.json').read_text());state=json.loads(Path('/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json').read_text());g=Genome(**state['members'][0]);kw=dict(blocked={t:frozenset(v) for t,v in p['blocked'].items()},membership={(d,t):v for d,t,v in p['membership']},risk_veto=p['risk_veto'],annual_cash_yield=p['cash_proxy_annual_yield'])
results=[]
for name,fn in [('original',old),('optimized',new)]:
 t=time.perf_counter();r=fn(prepared,g,**kw);results.append(r);print(name,'seconds',round(time.perf_counter()-t,3),'nav',r['final_nav'],'mdd',r['mdd_diagnostic'],flush=True)
assert results[0]==results[1], 'NUMERICAL_PARITY_FAILED'
print('FULL_RESULT_PARITY_PASS',flush=True)
