"""Bounded hand-authored fixtures; no historical or native-parity claims."""
from dataclasses import replace
import math
import pytest
from discovery.competitive_ga.functional_niche_manager import Candidate, NicheObservation, run_slice
from discovery.competitive_ga.native_signal_contract import NativeProposal
from engines.portfolio_replay.kernel import Bar, Replay, Signal
from engines.portfolio_selector.shared_selector_engine_contract_20261025 import CandidateDecision, select_entries
from engines.portfolio_selector.shared_selector_competition_20261025 import allocate

DATES = [f'2026-01-{i:02d}' for i in range(2, 10)]

def observation(t, d):
    return NicheObservation(d, '2025-12-31', 'SYNTHETIC_ONLY', (('special', .1), ('related', .2)))

def proposal(c, t, d, held, action=None, target=None):
    action = action or ('HOLD' if held else 'ENTER')
    target = target if target is not None else (held['weight'] if held else .1)
    return NativeProposal(d, t, c.family, c.chromosome_id, action, target, .1,
                          'entry_equity_fraction' if c.family == 'GA6' else 'net_return_fraction',
                          'SYNTHETIC_GENOME', 'SYNTHETIC_FEATURES', '2025-12-31')

def replay(days=None, candidates=None, **kw):
    return run_slice(days or [(d, {'A': Bar(100, 100)}) for d in DATES[:3]],
                     candidates or [Candidate('s', 'GA7', 'special', .02, .03)],
                     classify=kw.pop('classify', observation), eligible=kw.pop('eligible', lambda *a: True),
                     native=kw.pop('native', proposal), conditional_ev=kw.pop('conditional_ev', lambda *a: .1), **kw)


def test_global_rank_under_shared_cash_and_costs():
    bars = {**{f'A{i}': Bar(100,100) for i in range(10)}, 'ZZZ': Bar(100,100)}
    r = replay([(d,bars) for d in DATES[:2]], conditional_ev=lambda c,t,*a: .9 if t=='ZZZ' else .01)
    assert r['ledger'][0][1] == 'ZZZ'
    assert len(r['owners']) == 10
    assert r['ledger'][0][0] == DATES[1]
    assert sum(q*p+f for _,_,side,q,p,f in r['ledger'] if side=='BUY') == pytest.approx(100000)
    assert all(n[2] >= -1e-8 for n in r['nav'])


@pytest.mark.parametrize('gates,expected', [({'s':True,'r':True,'t':True},'s'),
    ({'s':False,'r':True,'t':True},'r'), ({'s':False,'r':False,'t':True},'t'),
    ({'s':False,'r':False,'t':False},None)])
def test_niche_fallback_and_identical_positive_ev_gates(gates, expected):
    cs = [Candidate('s','GA7','special',.02,.03),Candidate('r','GA6','related',.02,.03),Candidate('t','GA7',None,.02,.03)]
    r = replay(candidates=cs, conditional_ev=lambda c,*a: {'s':.01,'r':.2,'t':.9}[c.chromosome_id] if gates[c.chromosome_id] else -.1)
    assert (next(iter(r['owners'].values()))[1] if r['owners'] else None) == expected


@pytest.mark.parametrize('ev',[None,0.,-.1])
def test_no_trade_without_positive_comparable_net_ev(ev):
    assert not replay(conditional_ev=None if ev is None else lambda *a:ev)['ledger']


@pytest.mark.parametrize('ev',[math.nan,math.inf,-math.inf])
def test_nonfinite_net_ev_rejected(ev):
    with pytest.raises(ValueError, match='finite'):
        replay(conditional_ev=lambda *a:ev)


def test_mandatory_ordinary_prefill_risk_gate_and_gap_stress():
    b=Replay(settlement_sessions=1)
    b.pending=[Signal('A','GA6','x',.1,stop_distance=.8,gap_risk=.8)]
    b.day(DATES[0],{'A':Bar(100,100)})
    a=b.risk_audit[-1]
    assert a['modeled_equity_loss'] <= .02+1e-12
    assert b.shares['A']*100/100000 == pytest.approx(.02/.802)
    assert a['gap_stress_equity_loss'] > .02
    assert a['gap_loss_guaranteed'] is False


def test_missing_gap_inputs_use_total_loss_and_open_equity_denominator():
    b=Replay()
    b.pending=[Signal('A','GA7','s',.1)]
    b.day(DATES[0], {'A':Bar(150,150)})
    assert b.shares['A']*150/100000 == pytest.approx(.02/1.002)
    r=replay(candidates=[Candidate('s','GA7','special',.02)])
    assert r['ledger'][0][3]*100/100000 <= .02/1.002+1e-10


def test_defense_close_flag_exit_next_open_and_sale_settlement():
    r=replay(defense_at_close=lambda d:d==DATES[1])
    assert [n[4] for n in r['nav']] == [False,True,False]
    assert [(f[0],f[2]) for f in r['ledger']] == [(DATES[1],'BUY'),(DATES[2],'SELL')]
    assert r['unsettled'] and not r['owners']
    assert r['liquidity']['unsettled_cash'] == pytest.approx(sum(v for _,v in r['unsettled']))


def test_explicit_safe_cash_fallback_no_invented_yield():
    r=replay(eligible=lambda *a:False)
    assert r['liquidity']['mode']=='SAFE_SETTLED_CASH_FALLBACK'
    assert not r['liquidity']['sgov_enabled']
    assert r['nav'][-1][1]==100000
    assert not r['ledger']


def test_cost_execution_prices_next_open_and_independent_nav_identity():
    def native(c,t,d,h):
        return proposal(c,t,d,h,'EXIT' if h else 'ENTER',0 if h else .1)
    bars=[(DATES[0],{'A':Bar(90,90)}),(DATES[1],{'A':Bar(100,105)}),(DATES[2],{'A':Bar(110,110)})]
    r=replay(bars,native=native,fees=.001,spread=.002,slippage=.002,impact=.001)
    buy,sell=r['ledger']
    assert buy[4]==pytest.approx(100*1.004)
    assert sell[4]==pytest.approx(110*.996)
    assert buy[3]==pytest.approx(sell[3])
    expected=100000+sell[3]*sell[4]-sell[5]-buy[3]*buy[4]-buy[5]
    assert r['nav'][-1][1]==pytest.approx(expected)
    assert r['nav'][-1][1] == pytest.approx(100000+sum(x['pnl'] for x in r['realized']))


def test_gap_crash_mdd_halts_admission_without_replacing_native_exit():
    bars={f'A{i:02d}':Bar(100,100) for i in range(10)}
    crash={t:Bar(50,50) for t in bars}
    r=replay([(DATES[0],bars),(DATES[1],bars),(DATES[2],crash),(DATES[3],crash)])
    assert r['max_drawdown'] > .20
    assert r['mdd_policy']['breached'] and not r['mdd_policy']['feasible']
    assert r['admission_halted']
    assert all(f[2]=='BUY' for f in r['ledger']) # HOLD retains native ownership.
    assert not any(f[0]>=DATES[2] for f in r['ledger'])
    assert r['owners']


def test_open_gap_blocks_pending_add_before_close_monitor():
    b=Replay(shares={'A':800},cash=20000,high_water=100000)
    b.pending=[Signal('B','GA7','b',.1,stop_distance=.02,gap_risk=.03)]
    b.day(DATES[0],{'A':Bar(50,50),'B':Bar(100,100)})
    assert b.admission_halted and 'B' not in b.shares


def test_lifecycle_owner_after_eligibility_loss_and_prefix_invariance():
    actions=['ENTER','HOLD','ADD','REDUCE','EXIT','ENTER']
    weights=[.04,.04,.08,.02,0,.04]
    def native(c,t,d,h):
        i=DATES.index(d)
        return proposal(c,t,d,h,actions[i],weights[i])
    kw=dict(native=native,eligible=lambda c,t,d:d==DATES[0])
    days=[(d,{'A':Bar(100,100)}) for d in DATES[:6]]
    full=replay(days,**kw); short=replay(days[:3],**kw)
    assert [f[2] for f in full['ledger']] == ['BUY','BUY','SELL','SELL']
    assert full['nav'][:3]==short['nav']
    assert full['ledger'][:len(short['ledger'])]==short['ledger']
    assert full['decisions'][:3]==short['decisions']
    assert not full['owners']


def test_ga6_zero_and_nonfinite_proposals():
    d=CandidateDecision('2020-01-03','A','x','n','ENTER',0,1,'on','2020-01-02')
    assert select_entries([d],{})==[]
    assert allocate([('A','x',0,1)],{},100000,100000)==[]
    for v in (math.nan,math.inf,-math.inf):
        with pytest.raises(ValueError):replace(d,score=v).validate()
        with pytest.raises(ValueError):allocate([('A','x',.1,v)],{},100000,100000)
    assert not replay(native=lambda c,t,d,h:proposal(c,t,d,h,'ENTER',0))['ledger']


def test_adds_and_entries_share_global_net_ev_priority():
    bars={t:Bar(100,100) for t in [*[f'A{i}' for i in range(9)],'ZZZ']}
    def native(c,t,d,h):
        if d==DATES[0] and t=='ZZZ':return None
        return proposal(c,t,d,h,'ADD' if h else 'ENTER',.1)
    r=replay([(d,bars) for d in DATES[:3]],native=native,
             conditional_ev=lambda c,t,d,*a:.9 if t=='ZZZ' else .01)
    third=[f for f in r['ledger'] if f[0]==DATES[2]]
    assert third[0][1]=='ZZZ'
    assert all(f[2]=='BUY' for f in third)


def test_sale_proceeds_cannot_fund_same_open_buys():
    b=Replay(cash=0,shares={'A':1000},settlement_sessions=1,high_water=100000)
    b.pending=[Signal('A','GA7','a',0),Signal('B','GA6','b',.1,score=1,stop_distance=.02,gap_risk=.03)]
    bars={'A':Bar(100,100),'B':Bar(100,100)}
    b.day(DATES[0],bars)
    assert [f[2] for f in b.ledger]==['SELL']
    assert b.cash==0 and b.unsettled==[(1,99900)]
    b.pending=[Signal('B','GA6','b',.1,score=1,stop_distance=.02,gap_risk=.03)]
    b.day(DATES[1],bars)
    assert b.ledger[-1][2]=='BUY' and not b.unsettled


def test_actual_gap_can_exceed_modeled_trade_loss():
    days=[(DATES[0],{'A':Bar(100,100)}),(DATES[1],{'A':Bar(100,100)}),(DATES[2],{'A':Bar(50,50)})]
    r=replay(days)
    assert r['risk_audit'][0]['modeled_equity_loss'] <= .02
    assert r['max_drawdown'] > .02
    assert len(r['ledger'])==1 # No synthetic stop replaces owner HOLD.
    assert r['risk_audit'][0]['gap_loss_guaranteed'] is False


def test_opening_mark_rechecks_close_sized_risk():
    b=Replay(cash=50000,shares={'OLD':500},high_water=100000)
    b.pending=[Signal('NEW','GA6','n',.1,score=1,stop_distance=.8,gap_risk=.8)]
    # A rising incumbent changes opening equity and the opening risk denominator.
    b.day(DATES[0],{'OLD':Bar(120,120),'NEW':Bar(250,250)})
    assert b.shares['NEW']*250/110000 == pytest.approx(.02/.802)
    assert b.risk_audit[-1]['modeled_equity_loss'] <= .02+1e-12


def test_lowest_tier_still_requires_eligibility_and_risk():
    c=Candidate('t','GA6',None,.02,1.)
    r=replay(candidates=[c])
    assert r['ledger'][0][3]*100/100000 == pytest.approx(.02/1.002)
    assert not replay(candidates=[c],eligible=lambda *a:False)['ledger']
    assert not replay(candidates=[c],conditional_ev=lambda *a:0)['ledger']


def test_mdd_latch_does_not_reset_after_recovery_or_block_native_exit():
    b=Replay(cash=20000,shares={'A':800},high_water=100000)
    b.day(DATES[0],{'A':Bar(50,50),'B':Bar(100,100)})
    b.pending=[Signal('A','GA7','a',0),Signal('B','GA7','b',.1,stop_distance=.02,gap_risk=.03)]
    b.day(DATES[1],{'A':Bar(110,110),'B':Bar(100,100)})
    assert b.admission_halted
    assert not b.shares
    assert b.ledger[-1][2]=='SELL'
