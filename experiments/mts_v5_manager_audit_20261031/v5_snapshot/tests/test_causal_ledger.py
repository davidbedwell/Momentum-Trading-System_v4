from datetime import date, timedelta
import pytest
from engines.counterfactual_learning.causal_ledger import CausalLedger, Decision, Outcome

def decision():
    return Decision("d1","2020-01-02","AAA","REJECT",False,"c1","GA7",
                    "snapshot-sha","regime-v1","niche-v1","NORMAL","rank")

def outcome(matured="2020-01-23",observed="2020-01-22"):
    return Outcome("d1",observed,matured,"replace",150.0,"replay-sha")

def test_future_outcome_unavailable_until_mature():
    l=CausalLedger();l.record_decision(decision());l.record_outcome(outcome())
    assert l.available("2020-01-22")==()
    assert l.learn("2020-01-22","policy-1")==()
    assert len(l.learn("2020-01-23","policy-1"))==1
    assert l.learning_events[0]["outcome_keys"]==()

def test_invalid_chronology_rejected():
    l=CausalLedger();l.record_decision(decision())
    with pytest.raises(ValueError):l.record_outcome(outcome("2020-01-03","2020-01-04"))
    with pytest.raises(ValueError):l.record_outcome(outcome("2019-12-30","2019-12-29"))

def test_duplicate_and_missing_provenance_rejected():
    l=CausalLedger();l.record_decision(decision())
    with pytest.raises(ValueError):l.record_decision(decision())
    with pytest.raises(ValueError):l.record_outcome(Outcome("d1","2020-01-20","2020-01-21","hold",1.0,""))
    l.record_outcome(outcome())
    with pytest.raises(ValueError):l.record_outcome(outcome())

def test_export_audit_log():
    l=CausalLedger();l.record_decision(decision());l.record_outcome(outcome())
    l.learn("2020-01-23","policy-2")
    s=l.export_jsonl()
    assert '"kind": "decision"' in s and '"kind": "outcome"' in s and '"kind": "learning"' in s
