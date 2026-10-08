"""Construct fold-scoped execution inputs from aligned rows."""
import numpy as np
from .ga4_discovery_inputs import prepare_discovery_frame

def build_discovery_execution(stock_local, raw, membership):
    from .stage2_path_v3 import build_execution_paths, build_prospective_costs
    predictors, aligned, scope = prepare_discovery_frame(stock_local, raw, membership)
    paths = build_execution_paths(aligned, max_horizon=63)
    costs = build_prospective_costs(aligned, paths)
    if paths.endpoint_return.shape != (len(predictors), 63):
        raise ValueError('Execution paths misaligned')
    clusters = aligned.security_id.astype(str).to_numpy()
    if not np.array_equal(clusters, predictors.security_id.astype(str).to_numpy()):
        raise ValueError('Cluster alignment mismatch')
    return predictors, paths, costs, clusters, scope
