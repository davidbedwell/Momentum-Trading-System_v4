import numpy as np
from Core.layered_ga.stage2_calibration_shapes_v3 import SHAPES, planted_profile


def test_all_shapes_cover_63_horizons_and_frozen_plateaus():
    for name, (a, b, c, d) in SHAPES.items():
        p = planted_profile(name)
        assert p.shape == (63,)
        assert np.isfinite(p).all()
        assert np.all((0 <= p) & (p <= 1))
        assert np.allclose(p[b - 1:c], 1)
        assert p[d - 1] == 0
        assert p[-1] == 0


def test_fast_day_one_is_zero_and_not_duplicate_interpolation():
    p = planted_profile("FAST")
    assert p[0] == 0
    assert 0 < p[1] < 1
    assert p[2] == 1


def test_profiles_do_not_mutate_shape_definitions():
    before = dict(SHAPES)
    planted_profile("MEDIUM")
    assert SHAPES == before
