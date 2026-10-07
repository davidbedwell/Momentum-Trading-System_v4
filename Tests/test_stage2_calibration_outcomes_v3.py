import numpy as np
import pytest

from Core.layered_ga.stage2_path_v3 import ExecutionPaths, ProspectiveCosts
from Core.layered_ga.stage2_calibration_outcomes_v3 import (
    OutcomeOnlyCurveEvaluator, plant_endpoint_outcomes, response_delta
)


class StubCompiler:
    def __init__(self, mask):
        self.mask = mask

    def compile(self, family, genome):
        return self.mask


def _fixture():
    n, h = 400, 63
    endpoint = np.zeros((n, h), dtype=np.float32)
    low = np.full((n, h), -.005, dtype=np.float32)
    high = np.full((n, h), .005, dtype=np.float32)
    days = np.ones((n, h), dtype=np.int16)
    paths = ExecutionPaths(endpoint, low, high, days)
    z = np.zeros((n, h), dtype=np.float32)
    costs = ProspectiveCosts(z, z, np.zeros(n), np.zeros(n), np.ones(n), np.zeros(n))
    target = np.zeros(n, dtype=bool)
    target[:200] = True
    profile = np.zeros(h)
    profile[9:20] = 1
    return paths, costs, target, profile


def test_outcome_plant_preserves_input_and_exact_null():
    paths, costs, target, profile = _fixture()
    null = plant_endpoint_outcomes(paths, target, profile, 0)
    assert np.array_equal(null.paths.endpoint_return, paths.endpoint_return)
    assert not np.shares_memory(null.paths.endpoint_return, paths.endpoint_return)
    assert null.target_rows == 200


def test_only_target_rows_and_selected_horizons_change():
    paths, costs, target, profile = _fixture()
    planted = plant_endpoint_outcomes(paths, target, profile, .02)
    assert np.allclose(planted.paths.endpoint_return[:200, 9:20], .02)
    assert np.all(planted.paths.endpoint_return[200:] == 0)
    assert np.all(planted.paths.endpoint_return[:, :9] == 0)
    assert np.all(paths.endpoint_return == 0)


def test_outcome_only_adapter_evaluates_all_63_horizons_and_matched_null():
    paths, costs, target, profile = _fixture()
    clusters = np.arange(400, dtype=np.int32)
    compiler = StubCompiler(target)
    null_ev = OutcomeOnlyCurveEvaluator(compiler, paths, costs, clusters).evaluate("MOMENTUM", {}, "LONG")
    planted = plant_endpoint_outcomes(paths, target, profile, .02)
    planted_ev = OutcomeOnlyCurveEvaluator(compiler, planted.paths, costs, clusters).evaluate("MOMENTUM", {}, "LONG")
    differences = response_delta(planted_ev, null_ev)
    assert len(differences) == 63
    assert np.isclose(differences[9]["delta_ev_net"], .02, atol=1e-6)
    assert np.isclose(differences[0]["delta_ev_net"], 0, atol=1e-6)
    assert planted_ev.points[9]["lcb95"] > 0


def test_plant_rejects_misaligned_inputs():
    paths, costs, target, profile = _fixture()
    with pytest.raises(ValueError):
        plant_endpoint_outcomes(paths, target[:-1], profile, .02)
    with pytest.raises(ValueError):
        plant_endpoint_outcomes(paths, target, profile[:-1], .02)
