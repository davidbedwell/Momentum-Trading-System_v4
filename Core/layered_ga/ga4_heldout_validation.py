"""Independent out-of-sample GA4 candidate validation primitives.

Candidate selection must occur exclusively on development rows. This module
scores frozen selected masks on separately supplied heldout outcome rows and
compares them with a frozen null benchmark; it never selects on heldout.
"""
import hashlib
import json
import numpy as np

def validate_frozen_selection(candidate_mask, baseline_mask, heldout_returns,
                              heldout_clusters, *, selection_digest, min_clusters=20):
    candidate = np.asarray(candidate_mask, dtype=bool)
    baseline = np.asarray(baseline_mask, dtype=bool)
    returns = np.asarray(heldout_returns, dtype=float)
    clusters = np.asarray(heldout_clusters)
    if candidate.shape != baseline.shape or candidate.shape != returns.shape or returns.shape != clusters.shape:
        raise ValueError("heldout arrays not aligned")
    if not selection_digest:
        raise ValueError("missing frozen pre-heldout selection digest")
    valid = np.isfinite(returns)
    def score(mask):
        selected = mask & valid
        ids = np.unique(clusters[selected])
        if len(ids) < min_clusters:
            return {"clusters":int(len(ids)),"mean":None,"lcb95":None}
        means = np.array([returns[selected & (clusters == i)].mean() for i in ids])
        avg = float(means.mean())
        se = float(means.std(ddof=1) / np.sqrt(len(means)))
        return {"clusters":int(len(ids)),"mean":avg,"lcb95":avg - 1.96*se}
    a,b=score(candidate),score(baseline)
    usable=a["mean"] is not None and b["mean"] is not None
    return {"selection_digest":selection_digest,"candidate":a,"baseline":b,
            "mean_delta":a["mean"]-b["mean"] if usable else None,
            "heldout_pass": bool(usable and a["lcb95"] > b["mean"]),
            "independently_verified":False,
            "limitations":["Selection adjustment across all attempted genomes not established",
                           "External heldout split provenance and untouched status must be audited"]}

def digest_selection(genomes):
    return hashlib.sha256(json.dumps(genomes,sort_keys=True,separators=(",",":")).encode()).hexdigest()
