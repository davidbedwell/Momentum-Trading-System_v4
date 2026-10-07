import json,random,sys,time,traceback
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
source_preflight=verify_recovered_sources()
if source_preflight['decision']!='PASS':
 raise RuntimeError('certified recovered Stage-2 sources missing or hash-mismatched: '+json.dumps(source_preflight))
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces,VectorSignalCompiler,CERTIFIED_ROOT
from Core.layered_ga.stage2_data_v3 import load_path_cache
from Core.layered_ga.stage2_calibration_ga_adapter_v3 import MatchedEvaluator as OutcomeMatchedEvaluator
from Core.layered_ga.stage2_calibration_outcomes_v3 import plant_endpoint_outcomes
from Core.layered_ga.stage2_evaluator_v3 import cluster_ids_from_frame
from Core.layered_ga.stage2_calibration_gate_v3 import certify_calibration
from Core.layered_ga.stage2_calibration_shapes_v3 import planted_profile
sys.path.insert(0,str(CERTIFIED_ROOT))
from MTS_V4.computational_search import Candidate,Evaluation,EvolutionaryConfig,EvolutionarySearchOptimizer,SearchRunRequest
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration';CACHE=CAL.parent/'cache'
SHAPES={'FAST':(1,3,7,12),'MEDIUM':(3,10,20,30),'SLOW':(8,25,45,60)}
def save(n,x):
 p=CAL/n;t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2,allow_nan=False));t.replace(p)
def state(s,**kw):save('status.json',{'state':s,'updated':time.time(),**kw})
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
    profile=planted_profile(shape)
    planted=plant_endpoint_outcomes(paths,target,profile,effect)
    ev=OutcomeMatchedEvaluator(compiler,planted.paths,costs,cluster_ids_from_frame(df))
    baseline_curve=ev.curves.evaluate(family,entry['genome'],'LONG')
    baseline=max((p['lcb95'] for p in baseline_curve.points if np.isfinite(p.get('lcb95',np.nan))),default=-1e6)
    req=SearchRunRequest(run_id=f'{family}-{shape}-{effect}',optimizer_id='search.evolutionary.v1',search_space=spaces[family],evidence_identity='PLANTED',scientific_cohort='DISCOVERY',budget_evaluations=256,seed=rng.randrange(2**31))
    run=EvolutionarySearchOptimizer(EvolutionaryConfig()).run(req,ev)
    if ev.calls != len(ev.ledger):raise RuntimeError('GA evaluation ledger inconsistent')
    result={'family':family,'shape':shape,'effect':effect,'baseline':baseline,'best_ga':ev.best,'ga_evaluation_count':ev.calls,'baseline_excluded_from_ga':True,'full_63_day_curve':all(x['horizons']==63 for x in ev.ledger),'certified':False,'unique':run.unique_count,'target_visited':any(e.genome==entry['genome'] for e in run.ledger)}
    results.append(result);save('evolutionary_results.json',{'cases':results,'completed':len(results),'total':45})
 save('gate_diagnostic.json',certify_calibration(results,frozen_parameters_verified=False))
 state('STOPPED_ENGINEERING_MULTI_OBJECTIVE_AND_STATISTICAL_GATE_PENDING',completed=len(results),total=45)
if __name__=='__main__':
 try:main()
 except Exception as e:
  save('evolutionary_failure.json',{'error':repr(e),'traceback':traceback.format_exc()});state('ERROR',reason=repr(e));raise
