"""Align fold-local predictor and price rows before outcome construction."""
import pandas as pd
from .ga4_fold_predictors import rebuild_fold_predictors
from .ga4_fold_isolation import forbid_heldout_feedback

def prepare_discovery_frame(stock_local, raw, membership, phase='DEV80'):
    forbid_heldout_feedback(phase, selection_or_tuning=True)
    predictors, scope = rebuild_fold_predictors(stock_local, membership, phase)
    allowed = set(membership['dev80'])
    raw = raw.loc[raw.security_id.astype(str).isin(allowed)].copy()
    pred_keys = predictors[['security_id', 'effective_date']].copy()
    raw_keys = raw[['security_id', 'date']].rename(columns={'date': 'effective_date'})
    for frame in (pred_keys, raw_keys):
        frame['security_id'] = frame.security_id.astype(str)
        frame['effective_date'] = pd.to_datetime(frame.effective_date)
        if frame.duplicated(['security_id', 'effective_date']).any():
            raise ValueError('Duplicate security/date identity')
    if set(map(tuple, pred_keys.to_numpy())) != set(map(tuple, raw_keys.to_numpy())):
        raise ValueError('Predictor and raw identities differ')
    raw['security_id'] = raw.security_id.astype(str)
    raw['effective_date'] = pd.to_datetime(raw.date)
    raw = raw.set_index(['security_id', 'effective_date']).loc[pd.MultiIndex.from_frame(pred_keys)].reset_index()
    return predictors, raw, scope

[executed on device: instance-e298gycb-main (a21f8a9b-b225-483b-b45f-ba34708f98ee)]