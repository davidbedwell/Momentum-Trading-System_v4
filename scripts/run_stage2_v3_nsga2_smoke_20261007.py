"""Real full-path GA smoke experiment. Not a scientific certificate."""
import json,sys,hashlib
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

def main():
    assert verify_recovered_sources()['decision']=='PASS'
    cal=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
    targets=json.loads((cal/'target_manifest.json').read_text())['targets']
    family=next(iter(targets));effect=.02;shape='FAST'
    cache=cal.parent/'cache';df=pd.read_parquet(cache/'dev117_predictors_v3.parquet')
    paths,costs=load_path_cache(cache);compiler=VectorSignalCompiler(df)
    target=compiler.compile(family,targets[family]['genome'])
    planted=plant_endpoint_outcomes(paths,target,planted_profile(shape),effect)
    evaluator=OutcomeOnlyCurveEvaluator(compiler,planted.paths,costs,cluster_ids_from_frame(df))
    run=evolve(stage2_search_spaces()[family],lambda genome:evaluator.evaluate(family,genome,'LONG'),seed=20261007,population_size=8,generations=2)
    artifact={'method':run['method'],'generations':run['generations'],'unique_evaluations':run['unique_evaluations'],
              'heldout_selection_adjusted_validation':None,'certification':'NOT_CERTIFIED_SMOKE'}
    dest=cal/'nsga2_smoke_evolutionary_ledger.json';dest.write_text(json.dumps(artifact,allow_nan=True))
    print(json.dumps({'ledger':str(dest),'family':family,'unique_evaluations':run['unique_evaluations'],
                      'generations':len(run['generations']),'independent_audit_failures':audit_evolutionary_ledger(artifact)}))
if __name__=='__main__':main()
