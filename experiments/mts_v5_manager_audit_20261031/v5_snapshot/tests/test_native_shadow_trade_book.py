from discovery.competitive_ga.native_shadow_trade_book import ShadowBook
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar

def signal(day,action):
    return NativeProposal(day,'AAA','GA6','c',action,.1 if action=='ENTER' else 0.,
        .1,'entry_equity_fraction','source','snapshot','2026-01-01')

def test_shadow_outcome_only_after_next_open_exit():
    book=ShadowBook(fee=.001)
    book.close_session(0,[signal('2026-01-02','ENTER')])
    assert book.open_session(1,{'AAA':Bar(100,110)})==[]
    assert book.open_session(2,{'AAA':Bar(110,120)})==[]
    book.close_session(2,[signal('2026-01-06','EXIT')])
    assert book.completed==[]
    matured=book.open_session(3,{'AAA':Bar(120,130)})
    assert len(matured)==1
    assert matured[0].decision_session==1 and matured[0].maturity_session==3
    assert abs(matured[0].net_r-(120*.999/(100*1.001)-1))<1e-12

def test_no_implicit_exit_from_missing_signals():
    book=ShadowBook()
    book.close_session(0,[signal('2026-01-02','ENTER')])
    book.open_session(1,{'AAA':Bar(100,100)})
    book.close_session(1,[])
    assert not book.open_session(2,{'AAA':Bar(80,80)})
    assert len(book.positions)==1
