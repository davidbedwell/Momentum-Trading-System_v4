import json,sys,importlib.util,math
from pathlib import Path
sys.path.insert(0,'/opt/mts');sys.path.insert(0,'/opt/mts/ga5_redesign')
import pandas as pd
from ga5_redesign.guarded_evaluator_niche_single_exit import PreparedSessions
from ga5_chromosome_contract import Genome
from ga6.guarded_evaluator_ga6 import evaluate as new
root=Path('/opt/mts/ga5_redesign');frame=pd.read_parquet(root/'exploratory79_ga4_enriched.parquet');frame=frame[(frame.date>='2005-09-14')&(frame.date<'2026-09-15')];prepared=PreparedSessions(frame)
policy=json.loads((root/'exploratory79_policy.json').read_text());state=json.loads(Path('/opt/mts/ga6/runs/ga6_production_v1/checkpoint_unified.json').read_text());genome=Genome(**state['members'][0])
spec=importlib.util.spec_from_file_location('ga6_old_core','/opt/mts/ga6/guarded_evaluator_before_capacity_cache_20261021.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
args=(prepared,genome);kwargs=dict(blocked={t:frozenset(v) for t,v in policy['blocked'].items()},membership={(d,t):v for d,t,v in policy['membership']},risk_veto=policy['risk_veto'],annual_cash_yield=policy['cash_proxy_annual_yield'],niche_labels=None)
a=mod.evaluate(*args,**kwargs);b=new(*args,**kwargs)
def compare(x,y,path='root'):
 if isinstance(x,dict):
  assert isinstance(y,dict) and x.keys()==y.keys(),(path,'keys');[compare(v,y[k],path+'.'+str(k)) for k,v in x.items()]
 elif isinstance(x,(list,tuple)):
  assert isinstance(y,(list,tuple)) and len(x)==len(y),(path,'length');[compare(v,w,path+'['+str(i)+']') for i,(v,w) in enumerate(zip(x,y))]
 elif isinstance(x,(int,float)) and not isinstance(x,bool):
  assert isinstance(y,(int,float)) and (math.isclose(x,y,rel_tol=1e-12,abs_tol=1e-12) or (math.isnan(x) and math.isnan(y))),(path,x,y)
 else:assert x==y,(path,x,y)
compare(a,b);print('CORE_PARITY_PASS',len(a['shadow']['trades']),'trades',flush=True)
