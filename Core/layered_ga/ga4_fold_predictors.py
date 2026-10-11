"""Recompute cross-sectional predictors after security-fold isolation."""
from __future__ import annotations

from .ga4_fold_isolation import assert_fold_scoped_frame
from .stage2_features_v3 import recompute_cross_sectional, CROSS_COLUMNS


def rebuild_fold_predictors(stock_local, membership, phase):
    """Accept stock-local predictors only; reject cached all-universe columns."""
    if phase not in ("DEV80", "DEV37"):
        raise ValueError("Invalid phase")
    if any(column in stock_local.columns for column in CROSS_COLUMNS):
        raise ValueError("Cross-sectional columns already present in stock-local input")
    expected = set(membership["dev80" if phase == "DEV80" else "dev37"])
    subset = stock_local.loc[stock_local["security_id"].astype(str).isin(expected)].copy()
    scope = f"{membership['membership_sha256']}:{phase}:recomputed"
    assert_fold_scoped_frame(subset, membership, phase, predictor_scope=scope)
    result = recompute_cross_sectional(subset)
    assert_fold_scoped_frame(result, membership, phase, predictor_scope=scope)
    return result, scope
