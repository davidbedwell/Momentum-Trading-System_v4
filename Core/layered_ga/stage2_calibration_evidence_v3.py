"""Strict calibration evidence builder: compute measurable claims, never invent PASS.

This is an intermediate diagnostic. Statistical selection-bias corrections,
cross-case independent replication and certified budget remain separate gates.
"""
from __future__ import annotations
import numpy as np


def stable_plateau_horizons(points, *, minimum_ratio=.95):
    """Find contiguous high-response regions, not isolated single-day maxima."""
    eligible = [(int(p["horizon"]), float(p["ev_net"])) for p in points
                if np.isfinite(p.get("ev_net", np.nan))]
    if not eligible:
        return ()
    peak = max(v for _, v in eligible)
    if peak <= 0:
        return ()
    selected = [h for h, v in eligible if v >= minimum_ratio * peak]
    groups = []
    for h in selected:
        if groups and h == groups[-1][-1] + 1:
            groups[-1].append(h)
        else:
            groups.append([h])
    return tuple(tuple(g) for g in groups if len(g) >= 2)


def target_region_evidence(curve, true_window, *, min_effective_n):
    """Report direct full-path observations, with no preemptive PASS decision."""
    lo, hi = (int(x) for x in true_window)
    points = [p for p in curve.points if lo <= int(p["horizon"]) <= hi]
    sufficient = [p for p in points
                  if p.get("effective_n", 0) >= min_effective_n
                  and np.isfinite(p.get("lcb95", np.nan))]
    plateaus = stable_plateau_horizons(curve.points)
    overlap = any(sum(lo <= h <= hi for h in g) >= 2 for g in plateaus)
    return {
        "observed_positive_lcb95": any(p["lcb95"] > 0 for p in sufficient),
        "observed_effective_n_min": min((p.get("effective_n", 0) for p in sufficient), default=0),
        "observed_stable_plateau_overlap": overlap,
        "plateau_regions": [list(g) for g in plateaus],
        "region_horizons": [p["horizon"] for p in points],
    }
