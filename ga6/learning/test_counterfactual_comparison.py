import pytest
from ga6.learning.counterfactual_comparison import link_fills_to_signals,compare_completed_shadow_trades

def signal(action="ENTER"):
    return dict(decision_date="2024-01-02",symbol="AAA",
                evidence_cutoff="2024-01-02",action=action)
def fill():
    return dict(decision_date="2024-01-02",execution_date="2024-01-03",
                security="AAA",side="BUY",quantity=10)
def test_signal_link():
    result=link_fills_to_signals([fill()],[signal()],run_id="r",chromosome_id="2")
    assert result[0]["attribution_status"]=="SIGNAL_ACTION_MATCHED"
    assert result[0]["decision_id"]=="r:2:2024-01-02:AAA"
def test_risk_override_not_discretionary():
    result=link_fills_to_signals([dict(fill(),side="SELL")],[signal()],run_id="r",chromosome_id="2")
    assert result[0]["attribution_status"]=="EXECUTION_OVERRIDE_OR_RISK_EXIT"
def test_duplicate_identity_rejected():
    with pytest.raises(ValueError,match="duplicate"):
        link_fills_to_signals([], [signal(),signal()],run_id="r",chromosome_id="2")
def test_maturity_comparison():
    a=dict(symbol="AAA",entry_decision_date="2024-01-02",
           exit_date="2024-01-09",net_return=.05,realized_pnl=50,holding_sessions=5)
    b=dict(a,net_return=.03,realized_pnl=30)
    assert not compare_completed_shadow_trades({"1":[a],"2":[b]},as_of="2024-01-09")
    result=compare_completed_shadow_trades({"1":[a],"2":[b]},as_of="2024-01-10")
    assert [x["chromosome"] for x in result[0]["candidates"]]==["1","2"]
