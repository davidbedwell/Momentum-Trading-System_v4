"""Adversarial accounting fixtures, not synthetic-market research evidence."""
import sys
from types import SimpleNamespace
import pytest
from discovery.competitive_ga.ga7_ledger_bridge import replay


def genome(**overrides):
    return SimpleNamespace(**dict(dict(identity=lambda: 'frozen', capacity=8, stop_pct=.02,
        entry_pct=.1, feature_a='a', feature_b='b', exit_rule='signal_decay'), **overrides))


def bar(price=100., strength=.9, sector='s', **extra):
    return dict(open=price, close=price, low=price, eligible=True, sector=sector,
                features={'a':strength, 'b':strength}, **extra)


def native(g, sessions):
    sys.path.insert(0, '/opt/mts/ga7-deploy/ga7_unbounded')
    from ga7.request_replay import replay_requests
    return replay_requests(g, sessions, lambda g,b:b['features']['a']>.3,
                           cash_yield=0., record_pass=True)


def test_native_parity_sector_priority_dividend_reduce_and_exit():
    g=genome()
    sessions=[]
    for i in range(7):
        bars={t:bar(101+i, .4 if i==2 else (.1 if i==4 else .9),
                    dividend=2. if i==3 else 0.) for t in ('D','C','B','A')}
        sessions.append((f'2020-01-{i+1:02d}',bars,False))
    result, ledger=native(g,sessions)
    independent=replay(g,sessions,ledger.requests)
    assert independent['final_nav']==pytest.approx(result['final_nav'],abs=1e-8)
    assert {p['action'] for p in ledger.requests} >= {'ENTER','REDUCE','EXIT'}
    assert {f[1] for f in independent['fills'] if f[0]==1}=={'A','B','C'}
    assert independent['max_cashflow_residual']<1e-8
    assert any(kind=='DIVIDEND' and amount>0 for _,kind,amount in independent['journal'])


def request(i,t,action,weight=0.):
    return dict(session=i,ticker=t,action=action,requested_weight=weight,
                chromosome_id='frozen',probability=.8,expected_net_return=.1,
                downside_risk=.02,confidence=.8)


def test_one_share_reduce_and_unsettled_sales_cannot_fund_same_open():
    sessions=[(f'2020-01-0{i+1}',{'A':bar(), 'B':bar(sector='b')},False) for i in range(4)]
    tape=[request(0,'A','ENTER',.3),request(1,'A','REDUCE'),request(1,'B','ENTER',.3)]
    result=replay(genome(),sessions,tape,capital=334.)
    # 334*.3/(100*1.001) floors to one; half of one must liquidate.
    assert result['fills'][1][2:4]==('SELL',1)
    assert result['daily'][2]['receivable']==pytest.approx(99.9)
    assert result['daily'][3]['receivable']==0
    assert result['max_cashflow_residual']<1e-8
    # Full cash consumption makes the settlement restriction decisive.
    g=genome(stop_pct=.02)
    tape=[request(0,'A','ENTER',.3),request(1,'A','EXIT'),request(1,'B','ENTER',.3)]
    # Native cap .30 prevents spending all cash on one name; use four sectors.
    bars={t:bar(sector=t) for t in 'ABCDZ'}
    sessions=[(str(i),bars,False) for i in range(4)]
    tape=[request(0,t,'ENTER',.3) for t in 'ABCD']+[request(1,'A','EXIT'),request(1,'Z','ENTER',.3)]
    result=replay(g,sessions,tape,capital=1000.,fractional=True)
    assert not any(f[0]==2 and f[1]=='Z' for f in result['fills'])
    assert result['daily'][2]['receivable']>0


def test_next_close_cannot_change_open_fill_and_terminal_fee_identity():
    g=genome()
    tape=[request(0,'A','ENTER',.1)]
    runs=[]
    for close in (1.,999.):
        b=bar();b['close']=close
        sessions=[('1',{'A':bar()},False),('2',{'A':b},False)]
        result=replay(g,sessions,tape)
        marked=replay(g,sessions,tape,terminal_liquidation=False)
        assert marked['final_nav']-result['final_nav']==pytest.approx(result['terminal_fee'])
        runs.append(result['fills'][0])
    assert runs[0]==runs[1]


@pytest.mark.parametrize('damage', ['split','missing_held','duplicate','future','nan'])
def test_unsupported_or_incomplete_inputs_fail_closed(damage):
    sessions=[('1',{'A':bar()},False),('2',{'A':bar()},False),('3',{'A':bar()},False)]
    tape=[request(0,'A','ENTER',.1)]
    if damage=='split':sessions[1][1]['A']['split']=2
    if damage=='missing_held':sessions[2][1].clear()
    if damage=='duplicate':tape*=2
    if damage=='future':tape[0]['session']=2
    if damage=='nan':sessions[1][1]['A']['close']=float('nan')
    with pytest.raises(ValueError):replay(genome(),sessions,tape)
