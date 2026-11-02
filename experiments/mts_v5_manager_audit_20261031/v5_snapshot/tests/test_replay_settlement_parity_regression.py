"""Research-kernel settlement and accounting regression fixtures.
These are NOT broker or historical-data certification.
"""
from engines.portfolio_replay.kernel import Replay, Bar, Signal


def test_sale_proceeds_cannot_fund_same_open_purchase():
    r = Replay(cash=0., shares={"AAA": 100.})
    bars = {"AAA": Bar(100., 100.), "BBB": Bar(100., 100.)}
    r.pending = [Signal("AAA", "GA6", "exit", 0.), Signal("BBB", "GA7", "entry", .1)]
    r.day("d1", bars)
    assert not any(fill[1] == "BBB" and fill[2] == "BUY" for fill in r.ledger)
    assert r.cash > 0
    assert not r.shares


def test_previous_session_sale_cash_can_fund_next_open():
    r = Replay(cash=0., shares={"AAA": 100.})
    bars = {"AAA": Bar(100., 100.), "BBB": Bar(100., 100.)}
    r.pending = [Signal("AAA", "GA6", "exit", 0.), Signal("BBB", "GA7", "entry", .1)]
    r.day("d1", bars, [Signal("BBB", "GA7", "entry", .1)])
    r.day("d2", bars)
    assert any(fill[0] == "d2" and fill[1] == "BBB" and fill[2] == "BUY" for fill in r.ledger)


def test_family_neutral_dividend_and_split_accounting():
    def run(family):
        r = Replay(cash=90000., shares={"AAA": 100.})
        r.day("d1", {"AAA": Bar(50., 51., dividend=1., split=2.)})
        return r.cash, r.shares, r.nav
    assert run("GA6") == run("GA7")
    cash, shares, nav = run("GA6")
    assert shares["AAA"] == 200.
    assert cash == 90200.
    assert nav[-1][1] == 100400.
