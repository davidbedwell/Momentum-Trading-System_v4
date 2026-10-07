import json
from pathlib import Path
from Core.g3.nullgate import summarize_matched_pilot, authorization_state

def test_current_pilot_is_finite_matched_and_not_production_authorized():
    p=Path("Research/G3/MTS_G3_MATCHED_REAL_NULL_PILOT_20261006.json")
    x=json.loads(p.read_text())
    m=summarize_matched_pilot(x)
    assert m.matched_budget
    assert m.finite
    assert m.generations==6
    assert authorization_state(m)=="THRESHOLD_NOT_FROZEN_NO_PRODUCTION_AUTHORIZATION"

def test_current_pilot_real_median_wins_majority_of_generations():
    p=Path("Research/G3/MTS_G3_MATCHED_REAL_NULL_PILOT_20261006.json")
    x=json.loads(p.read_text())
    m=summarize_matched_pilot(x)
    assert m.real_wins_generations >= 4
    assert m.final_median_gap > 0
