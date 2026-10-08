"""Prospective, checkpointed 45-case evolutionary evidence run; never self-certifies."""
import json,sys,hashlib,time,traceback
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
from Core.layered_ga.stage2_compiler_v3 import stage2_search_spaces,VectorSignalCompiler
from Core.layered_ga.stage2_data_v3 import load_path_cache
from Core.layered_ga.stage2_calibration_outcomes_v3 import plant_endpoint_outcomes,OutcomeOnlyCurveEvaluator
from Core.layered_ga.stage2_calibration_shapes_v3 import planted_profile
from Core.layered_ga.stage2_evaluator_v3 import cluster_ids_from_frame
from Core.layered_ga.stage2_nsga2_engine_v3 import evolve
from Core.layered_ga.stage2_certification_evidence_v3 import audit_evolutionary_ledger
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
def atomic(path,obj):
 tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,allow_nan=True));tmp.replace(path)
def main():
 assert verify_recovered_sources()['decision']=='PASS'
 policy=json.loads((ROOT/'Research/Design/MTS_STAGE2_V3_CATASTROPHIC_POLICY_FREEZE_20261007.json').read_text())
 assert policy['status']=='FROZEN_FOR_NEW_SEARCH_NOT_CERTIFIED'
 targets=json.loads((CAL/'target_manifest.json').read_text())['targets']
 cache=CAL.parent/'cache';df=pd.read_parquet(cache/'dev117_predictors_v3.parquet')
 paths,costs=load_path_cache(cache);compiler=VectorSignalCompiler(df);clusters=cluster_ids_from_frame(df);spaces=stage2_search_spaces()
 out=CAL/'nsga2_batch_evolutionary_evidence.json'
 record=json.loads(out.read_text()) if out.exists() else {'status':'RUNNING_UNCERTIFIED','cases':[],'policy_hash':policy['policy_hash'],'started_at':time.time()}
 assert record['policy_hash']==policy['policy_hash']
 completed={(c['family'],c['shape'],c['effect']) for c in record['cases']}
 for family,entry in targets.items():
  target=compiler.compile(family,entry['genome'])
  for shape in ('FAST','MEDIUM','SLOW'):
   for effect in (0,.0025,.005,.01,.02):
    if (family,shape,effect) in completed:continue
    planted=plant_endpoint_outcomes(paths,target,planted_profile(shape),effect)
    ev=OutcomeOnlyCurveEvaluator(compiler,planted.paths,costs,clusters)
    seed=int.from_bytes(hashlib.sha256(f'{family}|{shape}|{effect}|v3-nsga2'.encode()).digest()[:4],'big')
    run=evolve(spaces[family],lambda g:ev.evaluate(family,g,'LONG'),seed=seed,population_size=8,generations=2)
    generations=run['generations'];assert len(generations)==2
    case={'family':family,'shape':shape,'effect':effect,'seed':seed,'generations':generations,'unique_evaluations':run['unique_evaluations'],'side':'LONG','certified':False}
    record['cases'].append(case);completed.add((family,shape,effect))
    record['completed']=len(completed);atomic(out,record)
    print('CASE_COMPLETE',len(completed),family,shape,effect,flush=True)
 record['status']='EVOLUTION_COMPLETE_INDEPENDENT_VALIDATION_PENDING';atomic(out,record)
if __name__=='__main__':
 try:main()
 except Exception:
  (CAL/'nsga2_batch_failure.txt').write_text(traceback.format_exc());raise
