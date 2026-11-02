"""Synthetic Horizons stress boundary: date overlap is never scenario linkage."""
import numpy as np
import pandas as pd
from .horizons_feature_reconstruction import EXTERNAL, raw_panel
from .horizons_feature_normalization import normalize


def build(frame, external, *, scenario_hash, contract, decision_times):
    required = ('source_hash', 'mapping_provenance', 'availability_contract', 'normalization_contract')
    if (not scenario_hash or contract.get('kind') != 'joint_synthetic_scenario' or
        contract.get('scenario_hash') != scenario_hash or
        any(not contract.get(k) for k in required)):
        raise ValueError('compatible synthetic stress provenance unavailable; historical date overlap is insufficient')
    if not {'date', 'available_at', *EXTERNAL} <= set(external):
        raise ValueError('missing stress values/publication times')
    if external.date.duplicated().any() or set(external.date) != set(frame.date):
        raise ValueError('stress must cover exact causal feature dates')
    if not np.isfinite(external[list(EXTERNAL)].to_numpy(dtype=float)).all():
        raise ValueError('invalid stress values')
    for row in external.to_dict('records'):
        cutoff = pd.Timestamp(decision_times.get(row['date']))
        available = pd.Timestamp(row['available_at'])
        if any(pd.isna(t) or t.tzinfo is None for t in (cutoff, available)) or available > cutoff:
            raise ValueError('stress publication is uncertified or after decision')
        if str(cutoff.date()) != str(row['date'])[:10]:
            raise ValueError('stress decision date mismatch')
    return normalize(raw_panel(frame, external))
