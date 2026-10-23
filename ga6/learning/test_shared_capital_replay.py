"""Shared-cash and fail-closed parity tests using the real settlement ledger."""
from ga6.learning.shared_capital_replay import replay_orders, verify_reference_parity
from settlement_ledger import SettledLedger
from mts_next_open_ledger_v1 import Order

DATES=["2025-01-02","2025-01-03","2025-01-06","2025-01-07"]
SESSIONS=[(d,{"AAA":10.0,"BBB":10.0},{"AAA":10.0,"BBB":10.0}) for d in DATES]
POLICY=dict(membership={(d,s):True for d in DATES for s in ("AAA","BBB")},
    earnings_allowed={(d,s):True for d in DATES for s in ("AAA","BBB")},
    risk_veto={d:True for d in DATES},corporate_actions={})
def run(proposals,**overrides):
    opts=dict(POLICY);opts.update(overrides)
    return replay_orders(SESSIONS,proposals,starting_cash=100,fee=.001,
        annual_cash_yield=0,ledger_class=SettledLedger,order_class=Order,
        max_positions=2,**opts)
def test_competing_trades_share_one_cash_account():
    p={"2025-01-02":[dict(symbol="AAA",chromosome="1",action="ENTER",weight=.8),
        dict(symbol="BBB",chromosome="2",action="ENTER",weight=.8)]}
    r=run(p)
    assert len(r["fills"])==2
    assert sum(f["shares"]*f["price"] for f in r["fills"])<=100
    assert set(r["owners"])=={"AAA","BBB"}
    assert r["status"].endswith("NOT_SELECTOR_CERTIFIED")
def test_settlement_blocks_same_day_reinvestment():
    p={"2025-01-02":[dict(symbol="AAA",chromosome="1",action="ENTER",weight=.99)],
       "2025-01-03":[dict(symbol="AAA",chromosome="1",action="EXIT",weight=1),
                      dict(symbol="BBB",chromosome="2",action="ENTER",weight=.99)]}
    r=run(p)
    assert any(x[1]=="BBB" and x[3]=="insufficient_settled_cash_or_allocation" for x in r["rejections"])
    assert not r["owners"]
def test_ownership_is_immutable():
    p={"2025-01-02":[dict(symbol="AAA",chromosome="1",action="ENTER",weight=.5)],
       "2025-01-03":[dict(symbol="AAA",chromosome="2",action="SCALE_IN",weight=.2)]}
    r=run(p)
    assert any(x[3]=="owner_mismatch" for x in r["rejections"])
def test_execution_day_defense_vetoes_pending_buy():
    p={"2025-01-02":[dict(symbol="AAA",chromosome="1",action="ENTER",weight=.5)]}
    risk=dict(POLICY["risk_veto"]);risk["2025-01-03"]=False
    r=run(p,risk_veto=risk)
    assert not r["fills"]
    assert any(x[3]=="defense" for x in r["rejections"])
def test_parity_rejects_daily_nav_mismatch():
    r=run({})
    ref={"metrics":{"calendar_nav":list(r["nav"])},"fills":[]}
    assert verify_reference_parity(ref,r)["status"]=="EXACT_FILL_AND_DAILY_NAV_PARITY"
    ref["metrics"]["calendar_nav"][1]=(DATES[1],999)
    try: verify_reference_parity(ref,r)
    except AssertionError: pass
    else: raise AssertionError("daily NAV drift must fail")
def test_parity_rejects_fill_mismatch():
    p={"2025-01-02":[dict(symbol="AAA",chromosome="1",action="ENTER",weight=.5)]}
    r=run(p)
    ref={"metrics":{"calendar_nav":r["nav"]},"fills":[dict(execution_date=f["execution_date"],
        security=f["security"],side=f["side"],quantity=f["shares"],price=f["price"],
        fee=f["fee"]) for f in r["fills"]]}
    assert verify_reference_parity(ref,r)["fills"]==1
    ref["fills"][0]["quantity"]+=1
    try: verify_reference_parity(ref,r)
    except AssertionError: pass
    else: raise AssertionError("fill drift must fail")
