from types import SimpleNamespace
import numpy as np
import pytest
from Core.layered_ga.stage2_paired_null_v3 import paired_effect_curve


def test_paired_null_and_plant_delta_across_all_horizons():
    n, h = 400, 63
    a = np.zeros((n, h), dtype=np.float32)
    b = a.copy()
    b[:200, 9:20] = .02
    z = np.zeros((n, h), dtype=np.float32)
    costs = SimpleNamespace(long_roundtrip=z, short_roundtrip=z)
    rows = paired_effect_curve(np.arange(n) < 200,
                               SimpleNamespace(endpoint_return=a),
                               SimpleNamespace(endpoint_return=b),
                               costs, np.arange(n))
    assert len(rows) == 63
    assert rows[0]["paired_delta_ev"] == 0
    assert np.isclose(rows[9]["paired_delta_ev"], .02)
    assert rows[9]["paired_delta_lcb95"] > 0


def test_null_cannot_have_artificial_positive_delta():
    z = np.zeros((200, 63), dtype=np.float32)
    costs = SimpleNamespace(long_roundtrip=z, short_roundtrip=z)
    rows = paired_effect_curve(np.ones(200, bool),
                               SimpleNamespace(endpoint_return=z),
                               SimpleNamespace(endpoint_return=z),
                               costs, np.arange(200))
    assert all(x["paired_delta_ev"] == 0 for x in rows)


def test_invalid_side_and_alignment_fail_closed():
    z = np.zeros((200, 63), dtype=np.float32)
    costs = SimpleNamespace(long_roundtrip=z, short_roundtrip=z)
    with pytest.raises(ValueError):
        paired_effect_curve(np.ones(200, bool),
                            SimpleNamespace(endpoint_return=z),
                            SimpleNamespace(endpoint_return=z),
                            costs, np.arange(200), side="UNKNOWN")
