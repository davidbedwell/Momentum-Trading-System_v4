from types import SimpleNamespace
from discovery.competitive_ga.native_shadow_trade_book import ShadowBook
from engines.portfolio_replay.kernel import Bar

def signal(action,weight):
    return SimpleNamespace(family='GA6',chromosome_id='x',ticker='AAA',action=action,target_weight=weight)

def test_native_shadow_add_reduce_exit_and_entry_context():
    book=ShadowBook(fee=.001)
    book.close_session(0,[signal('ENTER',.1)],{('GA6','x','AAA'):('NICHE_A','DISTANCE_NEAR')})
    assert book.open_session(1,{'AAA':Bar(100,100)})==[]
    key=('GA6','x','AAA')
    assert abs(book.positions[key]['units']-.000999)<1e-10
    book.close_session(1,[signal('ADD',.2)])
    book.open_session(2,{'AAA':Bar(105,105)})
    assert .19 < book.positions[key]['units']*105/(book.positions[key]['cash']+book.positions[key]['units']*105) < .21
    book.close_session(2,[signal('REDUCE',.05)])
    book.open_session(3,{'AAA':Bar(110,110)})
    assert .049 < book.positions[key]['units']*110/(book.positions[key]['cash']+book.positions[key]['units']*110) < .051
    book.close_session(3,[signal('EXIT',0)])
    outcomes=book.open_session(4,{'AAA':Bar(115,115)})
    assert len(outcomes)==1
    assert outcomes[0].context==('NICHE_A','DISTANCE_NEAR')
    assert outcomes[0].maturity_session==4
    assert outcomes[0].net_r>0
    assert not book.positions
