"""Verify no hindsight matching or premature learning labels."""
import pytest
from ga6.learning.shadow_learning_bridge import publish_matured_trades

class Ledger:
    def __init__(self):
        self.decisions=[];self.outcomes=[]
    def record_decision(self,**kw): self.decisions.append(kw)
    def record_outcome(self,**kw): self.outcomes.append(kw)

TRADE=dict(symbol="AAA",entry_decision_date="2024-01-02",
    entry_date="2024-01-03",exit_date="2024-01-10",holding_sessions=5,
    net_return=.05,realized_pnl=50.,gross_buy=1000.,gross_sell=1052.,
    fees=2.,fill_count=2,scale_in_count=0,scale_out_count=0)
DECISION=dict(decision_id="run:chrom:AAA:2024-01-02",
    asof="2024-01-02",evidence_cutoff="2024-01-02",action="ENTER",
    features={"momentum":.4},proposal={"risk":.01},selected=False)

def publish(ledger,as_of="2024-01-11",decisions=None):
    return publish_matured_trades(ledger,reconciled={"completed":[TRADE]},
        entry_decisions={(TRADE["symbol"],TRADE["entry_decision_date"]):DECISION}
        if decisions is None else decisions,chromosome_id="101",niche="NICHE-0001",
        as_of=as_of,run_id="run")

def test_matured_shadow_writes_original_snapshot():
    ledger=Ledger()
    assert publish(ledger)["inserted"]==1
    assert ledger.decisions[0]["selected"] is False
    assert ledger.outcomes[0]["outcome_asof"]=="2024-01-10"

def test_unmatured_is_deferred():
    ledger=Ledger()
    assert publish(ledger,as_of="2024-01-10")["deferred"]==1
    assert not ledger.decisions and not ledger.outcomes

def test_missing_original_decision_fails_closed():
    ledger=Ledger()
    with pytest.raises(ValueError,match="missing original"):
        publish(ledger,decisions={})
    assert not ledger.decisions and not ledger.outcomes

def test_future_features_rejected():
    ledger=Ledger()
    decision=dict(DECISION,evidence_cutoff="2024-01-04")
    with pytest.raises(ValueError,match="future evidence"):
        publish(ledger,decisions={("AAA","2024-01-02"):decision})
