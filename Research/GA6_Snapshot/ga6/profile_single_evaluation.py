import cProfile,pstats,io,json,time,sys
from pathlib import Path
sys.path.insert(0,'/opt/mts')
sys.path.insert(0,'/opt/mts/ga5_redesign')
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
from ga6.evaluator_adapter import evaluate
root=Path('/opt/mts/ga5_redesign');frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')]
prepared=PreparedSessions(frame)
policy=json.loads((root/'exploratory79_policy.json').read_text())
labels=pd.read_parquet(root/'dev79_niche_ga_v1'/'labels.parquet')
niche_labels={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for key in prepared.membership_keys:niche_labels.setdefault(key,None)
state=json.loads(Path('/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json').read_text())
genome=Genome(**state['members'][0]);p=cProfile.Profile();start=time.perf_counter();p.enable()
r=evaluate(prepared,genome,blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=None,evidence_labels=niche_labels)
p.disable();s=io.StringIO();pstats.Stats(p,stream=s).sort_stats('cumtime').print_stats(35)
Path('/opt/mts/ga6/runs/single_evaluation_profile.txt').write_text('elapsed='+str(time.perf_counter()-start)+'\n'+s.getvalue()+'\ntrades='+str(r['ga6_trade_metrics']['count']))
print('PROFILE_DONE',time.perf_counter()-start,flush=True)
