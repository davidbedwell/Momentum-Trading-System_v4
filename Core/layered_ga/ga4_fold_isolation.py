"""Fail-closed GA4 fold membership and data-scope validation.

Fold-specific predictor features must be computed after subsetting to the
allowed security IDs; filtering a full-universe rank/quantile after calculation
does not remove leakage.
"""
from __future__ import annotations

import hashlib
import json


def freeze_fold_membership(dev80, dev37):
    train = tuple(str(x) for x in dev80)
    heldout = tuple(str(x) for x in dev37)
    if len(train) != 80 or len(heldout) != 37:
        raise ValueError("GA4 fold requires exactly 80 discovery and 37 transport securities")
    if len(set(train)) != 80 or len(set(heldout)) != 37:
        raise ValueError("Duplicate security in fold")
    if set(train) & set(heldout):
        raise ValueError("DEV80/DEV37 overlap")
    payload = {"dev80": sorted(train), "dev37": sorted(heldout)}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"dev80": payload["dev80"], "dev37": payload["dev37"], "membership_sha256": digest}


def assert_fold_scoped_frame(frame, membership, phase, *, predictor_scope):
    """Reject cross-fold feature caches, including cached all-117 rankings."""
    if phase not in ("DEV80", "DEV37"):
        raise ValueError("Unknown fold phase")
    expected = set(membership["dev80" if phase == "DEV80" else "dev37"])
    actual = set(frame["security_id"].astype(str).unique())
    if actual != expected:
        raise ValueError(f"{phase} data membership mismatch; extra={sorted(actual - expected)} missing={sorted(expected - actual)}")
    if predictor_scope != f"{membership['membership_sha256']}:{phase}:recomputed":
        raise ValueError("Predictors not proven recomputed within fold")
    return True


def forbid_heldout_feedback(phase, *, selection_or_tuning):
    if phase == "DEV37" and selection_or_tuning:
        raise ValueError("Frozen DEV37 transport may not tune or select candidates")
