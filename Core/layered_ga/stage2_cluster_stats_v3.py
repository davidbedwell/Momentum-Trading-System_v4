"""Cluster-robust SE for row-weighted returns: independent-cluster sandwich."""
import math
import numpy as np


def row_weighted_cluster_se(values, cluster_ids):
    v = np.asarray(values, dtype=float)
    ids = np.asarray(cluster_ids)
    if v.ndim != 1 or ids.shape != v.shape or not np.isfinite(v).all():
        raise ValueError("invalid aligned return/cluster arrays")
    _, inv = np.unique(ids, return_inverse=True)
    counts = np.bincount(inv)
    sums = np.bincount(inv, weights=v)
    n, g = len(v), len(counts)
    if n == 0 or g < 2:
        return float("nan")
    ev = v.mean()
    return float(math.sqrt(g / (g - 1) * np.sum((sums - counts * ev) ** 2)) / n)
