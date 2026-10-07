from types import SimpleNamespace
import pytest
from Core.layered_ga.stage2_calibration_pareto_v3 import (
    Phenotype, nondominated_curve, dominates, describe_front
)


def test_pareto_preserves_tradeoff_instead_of_scalarizing():
    curve = SimpleNamespace(points=(
        {"horizon": 1, "ev_net": .03, "lcb95": .01, "mae_mean": -.05},
        {"horizon": 2, "ev_net": .02, "lcb95": .015, "mae_mean": -.01},
        {"horizon": 3, "ev_net": .01, "lcb95": .005, "mae_mean": -.08},
    ))
    assert [p.horizon for p in nondominated_curve(curve)] == [1, 2]
    assert len(describe_front(curve)) == 2


def test_matched_horizon_dominance():
    strong = Phenotype(10, .03, .02, -.01)
    weak = Phenotype(10, .02, .01, -.03)
    assert dominates(strong, weak)
    assert not dominates(weak, strong)
    with pytest.raises(ValueError):
        dominates(strong, Phenotype(11, .02, .01, -.03))


def test_nan_metrics_excluded():
    curve = SimpleNamespace(points=(
        {"horizon": 1, "ev_net": float("nan"), "lcb95": .01, "mae_mean": -.01},
        {"horizon": 2, "ev_net": .01, "lcb95": .001, "mae_mean": -.01},
    ))
    assert [p.horizon for p in nondominated_curve(curve)] == [2]
