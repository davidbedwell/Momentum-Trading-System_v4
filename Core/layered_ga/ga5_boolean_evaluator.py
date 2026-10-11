"""Stage2 incremental Boolean evaluation, isolated from immutable GA4."""
import json,hashlib
import numpy as np
from .ga5_boolean_grammar import validate,compile_mask,identity
from .stage2_evaluator_v3 import evaluate_curve,CurveEvaluation
from .ga4_discovery_evidence_policy import annotate_discovery
from .ga4_candidate_context_evidence import summarize_candidate_context

def evaluate_boolean(*,tree,arm,compiler,eligible,paths,costs,clusters,side,provenance,linked=None,reference=None):
    tree=validate(tree,arm)
    if side not in ('LONG','SHORT'):raise ValueError('Invalid side')
    mask=np.asarray(eligible)
    if mask.dtype!=np.dtype(bool) or mask.shape!=(len(compiler.frame),) or len(mask)!=len(clusters) or len(mask)!=len(paths.endpoint_return):raise ValueError('Misaligned DEV80 data')
    signal=compile_mask(tree,arm,compiler)
    if signal.shape!=mask.shape:raise ValueError('Misaligned Boolean signal')
    selected=mask & signal
    curve=evaluate_curve(selected,paths,costs,side,np.asarray(clusters),min_raw_n=200,min_effective_n=20)
    points=[dict(p) for p in curve.points]
    if [p['horizon'] for p in points]!=list(range(1,64)):raise ValueError('Incomplete evidence')
    cid=hashlib.sha256(json.dumps({'grammar':'GA5','arm':arm,'expression':tree,'side':side,'scope':'DEV80_ELIGIBLE'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
    record={'candidate_id':cid,'grammar_id':identity(tree,arm),'grammar_version':'GA5_INCREMENTAL_BOOLEAN_V1','expression':tree,'arm':arm,'context':{'scope':'DEV80_ELIGIBLE'},'fold':'DEV80','data_provenance':provenance,'side':side,'daily_horizon_evidence':points,'pareto_horizons':list(curve.pareto_horizons),'pareto_ranges':[list(x) for x in curve.pareto_ranges],'certified':False}
    if linked is not None:
        evidence=summarize_candidate_context(linked,selected,reference)
        record['stage1_context_reference']=evidence['reference'];record['stage1_candidate_context']=evidence
    return CurveEvaluation(curve.side,tuple(curve.points),tuple(curve.pareto_horizons),tuple(curve.pareto_ranges)),annotate_discovery(record)
