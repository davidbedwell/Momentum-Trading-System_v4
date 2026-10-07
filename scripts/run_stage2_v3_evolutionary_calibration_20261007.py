import json,random,sys,time,traceback
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces,VectorSignalCompiler,CERTIFIED_ROOT
from Core.layered_ga.stage2_data_v3 import load_path_cache
sys.path.insert(0,str(CERTIFIED_ROOT))
from MTS_V4.computational_search import Candidate,Evaluation,EvolutionaryConfig,EvolutionarySearchOptimizer,SearchRunRequest
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration';CACHE=CAL.parent/'cache'
SHAPES={'FAST':(1,3,7,12),'MEDIUM':(3,10,20,30),'SLOW':(8,25,45,60)}
def save(n,x):
 p=CAL/n;t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,allow_nan=False));t.replace(p)
def state(s,**kw):save('status.json',{'state':s,'updated':time.time(),**kw})
class MatchedEvaluator:
 analysis_contract_version='V3_MATCHED_RECOVERY_V1'
 def __init__(self,compiler,paths,costs,target,day,effect):
  self.compiler=compiler;self.paths=paths;self.costs=costs;self.target=target;self.day=day;self.effect=effect;self.calls=0;self.best=-1e9
 def evaluate(self,candidate,*,evidence_identity):
  mask=self.compiler.compile(candidate.family_id,candidate.genome);j=self.day-1
  valid=mask&np.isfinite(self.paths.endpoint_return[:,j])&np.isfinite(self.costs.long_roundtrip[:,j])
  n=int(valid.sum());score=float(self.effect*np.count_nonzero(valid&self.target)/n) if n>=200 else -1e6
  self.calls+=1;self.best=max(self.best,score)
  return Evaluation(candidate.candidate_id,evidence_identity,self.analysis_contract_version,{'net_expectancy':score})
def main():
 CAL.mkdir(parents=True,exist_ok=True);state('RUNNING_MATCHED_EVOLUTIONARY_SEARCH')
 targets=json.loads((CAL/'target_manifest.json').read_text())['targets']
 df=pd.read_parquet(CACHE/'dev117_predictors_v3.parquet');paths,costs=load_path_cache(CACHE)
 compiler=VectorSignalCompiler(df);spaces=stage2_search_spaces();rng=random.Random(20261007);results=[]
 for family,entry in targets.items():
  target=compiler.compile(family,entry['genome'])
  for shape,points in SHAPES.items():
   day=points[1]
   for effect in (.02,.01,.005,.0025,0.):
    state('RUNNING_MATCHED_EVOLUTIONARY_SEARCH',family=family,shape=shape,effect=effect,completed=len(results),total=45)
    ev=MatchedEvaluator(compiler,paths,costs,target,day,effect)
    baseline=ev.evaluate(Candidate.from_genome(family_id=family,genome=entry['genome'],proposal_source='TARGET_BASELINE'),evidence_identity='PLANTED')
    req=SearchRunRequest(run_id=f'{family}-{shape}-{effect}',optimizer_id='search.evolutionary.v1',search_space=spaces[family],evidence_identity='PLANTED',scientific_cohort='DISCOVERY',budget_evaluations=256,seed=rng.randrange(2**31))
    run=EvolutionarySearchOptimizer(EvolutionaryConfig()).run(req,ev)
    result={'family':family,'shape':shape,'effect':effect,'baseline':baseline.metrics['net_expectancy'],'best_ga':ev.best,'unique':run.unique_count,'target_visited':any(e.genome==entry['genome'] for e in run.ledger)}
    results.append(result);save('evolutionary_results.json',{'cases':results,'completed':len(results),'total':45})
 state('STOPPED_ENGINEERING_FULL_BUDGET_AND_STATISTICAL_GATE_PENDING',completed=len(results),total=45)
if __name__=='__main__':
 try:main()
 except Exception as e:
  save('evolutionary_failure.json',{'error':repr(e),'traceback':traceback.format_exc()});state('ERROR',reason=repr(e));raise
