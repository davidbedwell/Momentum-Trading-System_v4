import pytest
from ga6.learning.chronological_choice import choose_chromosome

def test_only_eligible_chromosome_can_win():
    s=dict(decision_date="2025-02-04",scores={"a":{"score":10},"b":{"score":2}})
    candidates=[dict(chromosome="b",decision_date="2025-02-04",evidence_cutoff="2025-02-03")]
    assert choose_chromosome(s,candidates)["selected"]["chromosome"]=="b"

def test_future_evidence_rejected():
    s=dict(decision_date="2025-02-04",scores={})
    with pytest.raises(ValueError):
        choose_chromosome(s,[dict(chromosome="a",decision_date="2025-02-04",
                                  evidence_cutoff="2025-02-05")])

def test_cold_start_explicit():
    s=dict(decision_date="2025-02-04",scores={})
    c=[dict(chromosome="a",decision_date="2025-02-04",evidence_cutoff="2025-02-04")]
    assert choose_chromosome(s,c)["selected"] is None
    assert choose_chromosome(s,c,fallback="a")["reason"]=="EXPLICIT_COLD_START_FALLBACK"
