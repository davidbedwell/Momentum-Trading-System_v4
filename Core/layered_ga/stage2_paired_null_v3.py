"""Paired cluster-robust planted-minus-null horizon evidence.

Diagnostic only: target identity belongs to the experiment auditor, never the
GA-facing evaluator. No multiple-testing correction or GA search-power claim.
"""
from __future__ import annotations
import numpy as np
from Core.layered_ga.stage2_cluster_stats_v3 import row_weighted_cluster_se


def paired_effect_curve(mask, original, planted, costs, cluster_ids, side="LONG", min_n=200, min_clusters=20):
    side = side.upper()
    if side not in ("LONG", "SHORT"):
        raise ValueError("invalid side")
    sign = 1.0 if side == "LONG" else -1.0
    a, b = original.endpoint_return, planted.endpoint_return
    cm = costs.long_roundtrip if side == "LONG" else costs.short_roundtrip
    mask = np.asarray(mask, bool)
    clusters = np.asarray(cluster_ids)
    if a.shape != b.shape or a.shape != cm.shape or mask.shape != (a.shape[0],) or clusters.shape != mask.shape:
        raise ValueError("unmatched planted/null arrays")
    output = []
    for j in range(a.shape[1]):
        valid = mask & np.isfinite(a[:, j]) & np.isfinite(b[:, j]) & np.isfinite(cm[:, j])
        n = int(valid.sum())
        g = int(np.unique(clusters[valid]).size)
        row = {"horizon": j + 1, "n": n, "effective_n": g,
               "paired_delta_ev": None, "paired_delta_lcb95": None}
        if n >= min_n and g >= min_clusters:
            delta = sign * (b[valid, j].astype(float) - a[valid, j].astype(float))
            # Costs cancel only because the same causal cost estimate applies
            # to each member of this matched pair.
            ev = float(delta.mean())
            se = row_weighted_cluster_se(delta, clusters[valid])
            row.update(paired_delta_ev=ev, paired_delta_lcb95=ev - 1.96 * se)
        output.append(row)
    return tuple(output)
