import sys,json,time,copy
from pathlib import Path
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
import ga6.evaluator_adapter as adapter
from ga6 import evaluator_adapter_pre_slice as old_adapter
from ga6 import guarded_evaluator_ga6_preperf_20261021 as old_core
from ga6 import prospective_replay_preperf as old_sim
from ga6 import policy_research_preperf_20261021 as old_policy
from ga6 import episode_uncertainty_preperf_20261021 as old_episode
import ga6.policy_evolution_oos as policy_oos
import ga6.niche_evidence as niche
root=Path('/opt/mts/ga5_redesign');frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')];prepared=PreparedSessions(frame)
policy=json.loads((root/'exploratory79_policy.json').read_text());labels=pd.read_parquet(root/'dev79_niche_ga_v1'/'labels.parquet');niche_labels={(str(r.date)[:10],r.ticker):r.research_niche for r in labels.itertuples(index=False)}
for key in prepared.membership_keys:niche_labels.setdefault(key,None)
state=json.loads(Path('/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json').read_text());g=Genome(**state['members'][0]);kw=dict(blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=None,evidence_labels=niche_labels)
originals=(adapter.ga6_raw_evaluate,policy_oos.evolve,policy_oos.evaluate_policy,niche.assess if hasattr(niche,'assess') else None)
import ga6.episode_uncertainty as episode
import ga6.policy_research as policy_research
import ga6.prospective_replay as replay
import ga6.evaluator_adapter_pre_slice as old_adapter
# The historical adapter uses its own imported core and module-global imports in its helpers.
old_adapter.ga6_raw_evaluate=old_core.evaluate
old_adapter.enrich.__globals__['__name__']='ga6.evaluator_adapter_pre_slice'
policy_oos.evolve=old_policy.evolve;policy_oos.evaluate_policy=old_policy.evaluate_policy
old_policy.evaluate_policy.__globals__['simulate']=old_sim.simulate
old_episode.assess.__globals__['__name__']='ga6.episode_uncertainty_preperf_20261021'
# Monkeypatch uncertainty only during original evaluation; restore for optimized.
import ga6.episode_uncertainty as ep
results=[]
for name,fn in [('original',old_adapter.evaluate),('optimized',adapter.evaluate)]:
 if name=='original':
  ep.assess=old_episode.assess;niche.assess=old_episode.assess if hasattr(niche,'assess') else None
 else:
  ep.assess=original_assess;policy_oos.evolve=original_evolve;policy_oos.evaluate_policy=original_evaluate
 t=time.perf_counter();r=fn(prepared,g,**kw);results.append(r);print(name,'elapsed',round(time.perf_counter()-t,3),'nav',r['final_nav'],'trades',r['ga6_trade_metrics']['count'],flush=True)
 if name=='original':
  original_assess=__import__('importlib').reload(ep).assess
  original_evolve=policy_research.evolve;original_evaluate=policy_research.evaluate_policy
def differences(a,b,path=''):
 if type(a)!=type(b):print('TYPE',path,type(a),type(b));return
 if isinstance(a,dict):
  for k in a.keys()|b.keys():
   if k not in a or k not in b:print('KEY',path,k);continue
   differences(a[k],b[k],path+'.'+str(k))
 elif isinstance(a,list):
  if len(a)!=len(b):print('LENGTH',path,len(a),len(b))
  for i,(x,y) in enumerate(zip(a,b)):differences(x,y,path+'['+str(i)+']')
 elif a!=b:print('VALUE',path,repr(a)[:100],repr(b)[:100])
differences(*results)
print('FULL_PARITY_PASS',flush=True)
