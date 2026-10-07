from types import SimpleNamespace
from Core.layered_ga.stage2_calibration_evidence_v3 import (
    stable_plateau_horizons, target_region_evidence
)


def test_isolated_one_day_peak_is_not_a_stable_plateau():
    points = [{"horizon": h, "ev_net": 1.0 if h == 10 else .1} for h in range(1, 64)]
    assert stable_plateau_horizons(points) == ()


def test_plateau_overlap_requires_two_days():
    points = [
        {"horizon": h, "ev_net": 1.0 if 10 <= h <= 20 else .1,
         "lcb95": .01 if 10 <= h <= 20 else -.01, "effective_n": 40}
        for h in range(1, 64)
    ]
    ev = target_region_evidence(SimpleNamespace(points=points), (10, 20), min_effective_n=20)
    assert ev["observed_positive_lcb95"]
    assert ev["observed_stable_plateau_overlap"]
    assert ev["observed_effective_n_min"] == 40


def test_effective_n_failure_is_not_a_positive_lcb_pass():
    points = [{"horizon": h, "ev_net": .01, "lcb95": .005, "effective_n": 2}
              for h in range(1, 64)]
    ev = target_region_evidence(SimpleNamespace(points=points), (10, 20), min_effective_n=20)
    assert not ev["observed_positive_lcb95"]
    assert ev["observed_effective_n_min"] == 0
