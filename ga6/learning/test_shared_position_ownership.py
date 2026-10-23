import pytest
from ga6.learning.shared_position_ownership import PositionOwners

def test_position_ownership_survives_ranking_changes():
    p=PositionOwners()
    p.record_fill(symbol="AAA",side="BUY",quantity=10,chromosome="A")
    p.record_fill(symbol="AAA",side="BUY",quantity=5,chromosome="A")
    assert p.owner("AAA")=="A"
    with pytest.raises(ValueError):
        p.record_fill(symbol="AAA",side="BUY",quantity=1,chromosome="B")
    p.record_fill(symbol="AAA",side="SELL",quantity=8)
    assert p.owner("AAA")=="A"
    p.reconcile({"AAA":7})
    p.record_fill(symbol="AAA",side="SELL",quantity=7)
    assert p.owner("AAA") is None
    p.reconcile({})

def test_reject_future_evidence_and_reconcile_mismatch():
    p=PositionOwners()
    with pytest.raises(ValueError):
        p.choose_entry(symbol="AAA",decision_date="2025-01-03",
            candidates=[dict(symbol="AAA",decision_date="2025-01-03",
                             evidence_cutoff="2025-01-04",chromosome="A")],
            scores={"A":1})
    p.record_fill(symbol="AAA",side="BUY",quantity=2,chromosome="A")
    with pytest.raises(ValueError):
        p.reconcile({"AAA":3})

def test_candidate_ranking_only_for_same_symbol():
    p=PositionOwners()
    result=p.choose_entry(symbol="AAA",decision_date="2025-01-03",
        candidates=[dict(symbol="BBB",decision_date="2025-01-03",
                         evidence_cutoff="2025-01-03",chromosome="A"),
                    dict(symbol="AAA",decision_date="2025-01-03",
                         evidence_cutoff="2025-01-03",chromosome="B")],
        scores={"A":5,"B":1})
    assert result["chromosome"]=="B"
