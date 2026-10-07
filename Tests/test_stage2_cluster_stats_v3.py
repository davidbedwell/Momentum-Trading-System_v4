import math
import numpy as np
from Core.layered_ga.stage2_cluster_stats_v3 import row_weighted_cluster_se


def test_unequal_cluster_sizes_use_row_weighted_center():
    v = np.array([0.0, 0.0, 0.0, 0.0, 1.0])
    groups = np.array([0, 0, 0, 0, 1])
    # The row-weighted EV is 0.2, not the mean of cluster means (0.5).
    # Cluster score residual sums are (-.8, .8).
    expected = math.sqrt(2 * (.8 ** 2 + .8 ** 2)) / 5
    assert np.isclose(row_weighted_cluster_se(v, groups), expected)


def test_permutation_invariance():
    v = np.array([.1, -.2, .3, .2, .1, -.1])
    groups = np.array([5, 5, 7, 8, 8, 9])
    p = np.array([5, 0, 3, 1, 4, 2])
    assert np.isclose(row_weighted_cluster_se(v, groups),
                      row_weighted_cluster_se(v[p], groups[p]))


def test_single_cluster_is_not_certifiable():
    assert math.isnan(row_weighted_cluster_se([.1, .2], [0, 0]))
