[Reading 30 lines from start (total: 30 lines, 0 remaining)]

"""Build complete-history outcomes and project onto DEV80 decision identities."""
from dataclasses import fields
import numpy as np
import pandas as pd
from .ga4_discovery_inputs import prepare_discovery_frame

def _project(obj, indices):
    return type(obj)(**{f.name: getattr(obj, f.name)[indices] for f in fields(obj)})

def build_discovery_execution(stock_local, raw, membership):
    from .stage2_path_v3 import build_execution_paths, build_prospective_costs
    from .stage2_evaluator_v3 import cluster_ids_from_frame
    predictors, full_raw, scope = prepare_discovery_frame(stock_local, raw, membership)
    raw_key = pd.MultiIndex.from_arrays([full_raw.security_id.astype(str), pd.to_datetime(full_raw.date)])
    decision_key = pd.MultiIndex.from_arrays([predictors.security_id.astype(str), pd.to_datetime(predictors.effective_date)])
    if not raw_key.is_unique or not decision_key.is_unique:
        raise ValueError('Duplicate execution identity')
    indices = raw_key.get_indexer(decision_key)
    if (indices < 0).any():
        raise ValueError('Missing execution decision identity')
    full_paths = build_execution_paths(full_raw, max_horizon=63)
    full_costs = build_prospective_costs(full_raw, full_paths)
    paths = _project(full_paths, indices)
    costs = _project(full_costs, indices)
    if paths.endpoint_return.shape != (len(predictors), 63) or costs.long_roundtrip.shape != (len(predictors), 63):
        raise ValueError('Execution paths/costs misaligned')
    clusters = cluster_ids_from_frame(predictors)
    if len(clusters) != len(predictors) or clusters.dtype.kind not in 'iu':
        raise ValueError('Cluster alignment mismatch')
    return predictors, paths, costs, clusters, scope

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]