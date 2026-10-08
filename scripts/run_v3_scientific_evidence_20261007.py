#!/usr/bin/env python3
"""Compute observed V3 target curves, paired null curves and independent diagnostics.
This does NOT certify evolutionary selection or authorize production.
Resumable by atomic per-case checkpoint, fail-closed.
"""
import hashlib,json,os,sys,time,traceback
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Core.layered_ga.stage2_recovered_source_preflight_v3 import verify_recovered_sources
from Core.layered_ga.stage2_compiler_v3 import VectorSignalCompiler
from Core.layered_ga.stage2_data_v3 import load_path_cache
from Core.layered_ga.stage2_evaluator_v3 import cluster_ids_from_frame
from Core.layered_ga.stage2_calibration_outcomes_v3 import OutcomeOnlyCurveEvaluator,plant_endpoint_outcomes,response_delta
from Core.layered_ga.stage2_calibration_shapes_v3 import planted_profile
from Core.layered_ga.stage2_calibration_evidence_v3 import target_region_evidence
from Core.layered_ga.stage2_calibration_gate_v3 import certify_calibration
CAL=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007/calibration'
CACHE=CAL.parent/'cache'
def atomic(path,obj):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(obj,indent=2,allow_nan=False));os.replace(tmp,path)
def finite(v):
    if isinstance(v,(float,np.floating)) and not np.isfinite(v):return None
    if isinstance(v,dict):return {k:finite(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)):return [finite(x) for x in v]
    if isinstance(v,np.generic):return v.item()
    return v
def main():
    assert verify_recovered_sources()['decision']=='PASS'
    targets=json.loads((CAL/'target_manifest.json').read_text())['targets']
    frame=pd.read_parquet(CACHE/'dev117_predictors_v3.parquet')
    compiler=VectorSignalCompiler(frame)
    paths,costs=load_path_cache(CACHE);clusters=cluster_ids_from_frame(frame)
    null=OutcomeOnlyCurveEvaluator(compiler,paths,costs,clusters)
    output=CAL/'observed_evidence.json'
    cases=json.loads(output.read_text()).get('cases',[]) if output.exists() else []
    completed={(x['family'],x['shape'],x['effect']) for x in cases}
    shapes={'FAST':(3,7),'MEDIUM':(10,20),'SLOW':(25,45)}
    for family,entry in targets.items():
        mask=compiler.compile(family,entry['genome'])
        baseline={side:null.evaluate(family,entry['genome'],side) for side in ('LONG','SHORT')}
        for shape,window in shapes.items():
            for effect in (0.,.0025,.005,.01,.02):
                if (family,shape,effect) in completed:continue
                planted=plant_endpoint_outcomes(paths,mask,planted_profile(shape),effect)
                evaluator=OutcomeOnlyCurveEvaluator(compiler,planted.paths,costs,clusters)
                sides={}
                for side in ('LONG','SHORT'):
                    curve=evaluator.evaluate(family,entry['genome'],side)
                    evidence=target_region_evidence(curve,window,min_effective_n=20)
                    delta=response_delta(curve,baseline[side])
                    sides[side]={'region':evidence,'paired_delta':finite(delta),'points':finite(curve.points)}
                case={'family':family,'shape':shape,'effect':effect,'target_baseline_evaluated':True,
                      'full_63_day_curve':all(len(sides[s]['points'])==63 for s in sides),
                      'long_short_evaluated_separately':True,'sides':sides,
                      'note':'descriptive paired baseline only; no selection-adjusted GA certification'}
                cases.append(case);completed.add((family,shape,effect))
                atomic(output,{'cases':cases,'completed':len(cases),'total':45,'scientific_certification':'PENDING'})
                atomic(CAL/'evidence_worker_status.json',{'state':'RUNNING','completed':len(cases),'total':45,'updated':time.time()})
    atomic(CAL/'evidence_worker_status.json',{'state':'EVIDENCE_COMPUTED_NOT_CERTIFIED','completed':len(cases),'total':45,'updated':time.time()})
    print('EVIDENCE_COMPUTED',len(cases),'CERTIFICATION_PENDING',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as exc:
        atomic(CAL/'evidence_worker_status.json',{'state':'ERROR','error':repr(exc),'traceback':traceback.format_exc()})
        raise
