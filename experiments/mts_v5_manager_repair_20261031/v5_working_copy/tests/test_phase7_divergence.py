"""Independent hand-calculated fixtures; no fixture is market evidence."""
import sys
from types import SimpleNamespace
import pytest
from discovery.competitive_ga.phase7_diagnostics import first_difference, common_request, observe_native


def test_first_divergence_preserves_order_missing_and_payload():
    assert first_difference(['A','B'], ['A','B']) is None
    assert first_difference(['A','B'], ['B','A']) == dict(index=0,native='A',shadow='B')
    assert first_difference(['A'], ['A','B']) == dict(index=1,native=None,shadow='B')
    assert first_difference([('A',2)], [('A',2.5)])['index']==0
    assert first_difference([], []) is None


@pytest.mark.parametrize('action,target', [('ENTER',.1),('ADD',.13),('INCREASE',.03),('REDUCE',.05),('EXIT',.1),('HOLD',.2),('UNKNOWN',None)])
def test_unsupported_common_semantics_fail_shut(action,target):
    with pytest.raises(ValueError,match='explicit share-order interface'):
        common_request(action,target=target)


def test_smallest_semantic_interface():
    assert common_request('EXIT',target=0)==('EXIT',0.)
    assert common_request('HOLD')==('HOLD',None)


def test_native_observation_against_dollar_oracle_and_restores_trace():
    sys.path.insert(0,'/opt/mts/ga7-deploy/ga7_unbounded')
    from ga7.request_replay import replay_requests
    g=SimpleNamespace(identity=lambda:'fixture',capacity=2,stop_pct=.02,
        entry_pct=.1,feature_a='a',feature_b='b',exit_rule='signal_decay')
    def bar(signal):
        return dict(open=100.,close=100.,low=100.,eligible=True,sector='s',features={'a':signal,'b':signal})
    panels=[(f'2020-01-0{i+1}',{'A':bar(signal)},False) for i,signal in enumerate((.9,.1,.1,.1))]
    _,_,states=observe_native(replay_requests,g,panels,lambda g,b:b['features']['a']>.5)
    # $10,000 budget / $100.10 floors to 99; $9,909.90 purchase.
    assert states[1]['cash']==pytest.approx(90090.1)
    assert states[1]['positions']['A']['shares']==99
    # Next open exit: $9,890.10 unavailable until following session.
    assert states[2]['cash']==pytest.approx(90090.1)
    assert states[2]['receivable']==pytest.approx(9890.1)
    assert states[2]['positions']=={}
    assert states[3]['cash']==pytest.approx(99980.2)
    assert states[3]['receivable']==0
    assert sys.gettrace() is None


def test_unsupported_native_observer_fails_before_call():
    def other():
        raise AssertionError('must never execute')
    with pytest.raises(ValueError,match='unsupported native observation'):
        observe_native(other,None,[],None)


def test_actual_first_fill_divergence_with_independent_priority_oracle():
    from discovery.competitive_ga.funded_shadow import FundedShadow
    from discovery.competitive_ga.phase4_native_smoke import DiagnosticAction
    from engines.portfolio_replay.kernel import Bar
    sys.path.insert(0,'/opt/mts/ga7-deploy/ga7_unbounded')
    from ga7.request_replay import replay_requests
    g=SimpleNamespace(identity=lambda:'fixture',capacity=1,stop_pct=.02,
        entry_pct=.1,feature_a='a',feature_b='b',exit_rule='signal_decay')
    bars={t:dict(open=100.,close=100.,low=100.,eligible=True,sector='s',
                features={'a':strength,'b':strength}) for t,strength in [('A',.6),('B',.9)]}
    panels=[('2020-01-01',bars,False),('2020-01-02',bars,False)]
    _,_,native=observe_native(replay_requests,g,panels,lambda g,b:True)
    owner=('GA7','fixture'); market={t:Bar(100.,100.) for t in bars}
    book=FundedShadow([owner],sessions=[p[0] for p in panels])
    book.open_session(0,market)
    book.close_session(0,[DiagnosticAction(panels[0][0],t,*owner,'ENTER',.1) for t in bars])
    book.open_session(1,market)
    # Higher native utility chooses B; capacity=1 rejects A. Shadow buys A first.
    assert list(native[1]['positions'])==['B']
    assert native[1]['positions']['B']['shares']==99
    assert book.fills[0][1][2]=='A'
    difference=first_difference(list(native[1]['positions']),[f[1][2] for f in book.fills])
    assert difference==dict(index=0,native='B',shadow='A')
