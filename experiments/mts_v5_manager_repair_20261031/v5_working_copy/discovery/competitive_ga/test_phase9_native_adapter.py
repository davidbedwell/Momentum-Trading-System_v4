"""Fixture evidence only: no market controls or model provenance asserted."""
from dataclasses import replace
from decimal import Decimal as D
import pytest
from discovery.competitive_ga.ga7_native_share_adapter import execute
from discovery.competitive_ga import ga7_native_kernels as kernels
from discovery.competitive_ga.native_style_share_executor import execute as reference
from discovery.competitive_ga.funded_share_executor import execute as funded
from discovery.competitive_ga.share_order_contract import Tape, Open, Order, Position, Receivable

CAL = tuple(f'2023-01-{day:02}' for day in range(2,12))


def fixture(n=3):
    orders = (
        Order(CAL[0],CAL[1],'GA7:a','A','BUY',1),  # ADD preexisting
        Order(CAL[0],CAL[1],'GA6:b','A','SELL',1), # REDUCE another owner
        Order(CAL[0],CAL[1],'GA6:b','B','BUY',10), # reject cash/capacity
        Order(CAL[1],CAL[2],'GA7:a','A','SELL',3), # EXIT
        Order(CAL[1],CAL[2],'GA6:b','A','SELL',2), # reject inventory
        Order(CAL[1],CAL[2],'GA6:b','B','BUY',2), # funded by prior T+1 sale; current EXIT remains pending
    )
    return Tape('fixed-shares-v1',CAL[:n+2],D(20),
        (Position('GA7:a','A',2,D(8),D('8.1'),7,D(12)),
         Position('GA6:b','A',2,D(9),D('9.1'),2,D(11))),
        (Receivable(CAL[1],D(1),'GA6:b'),),orders,
        tuple(Open(day,(('A',D(10)),('B',D(10))),day,('A','B')) for day in CAL[1:n+1]),
        D('.01'),'T+1',12)


def same_events(actual, expected):
    assert len(actual) == len(expected)
    for a,b in zip(actual,expected):
        assert (a.session,a.kind,a.owner,a.ticker,a.shares) == (b.session,b.kind,b.owner,b.ticker,b.shares)
        for attr in ('price','fee','cash','nav'):
            assert abs(getattr(a,attr)-getattr(b,attr)) < D('1e-10')
        assert [(r.due,r.owner) for r in a.receivables] == [(r.due,r.owner) for r in b.receivables]
        assert len(a.receivables) == len(b.receivables)
        for r,s in zip(a.receivables,b.receivables):
            assert abs(r.amount-s.amount) < D('1e-10')
        assert len(a.positions) == len(b.positions)
        for p,q in zip(a.positions,b.positions):
            assert (p.owner,p.ticker,p.shares,p.age) == (q.owner,q.ticker,q.shares,q.age)
            for attr in ('raw_entry','fee_basis','peak'):
                assert abs(getattr(p,attr)-getattr(q,attr)) < D('1e-10')


@pytest.mark.parametrize('n',range(2,9))
def test_native_kernels_against_both_independent_consumers(n):
    t = fixture(n)
    log = execute(t)
    same_events(log,reference(t)); same_events(log,funded(t))
    marks = [e for e in log if e.kind == 'MARK']
    # Hand: initial bank 21; ADD costs 10.1; REDUCE nets 9.9.
    # Next open settles 9.9, EXIT nets 29.7, B buy costs 20.2.
    assert abs(marks[0].cash-D('10.9')) < D('1e-12')
    assert abs(marks[0].nav-D('60.8')) < D('1e-12')
    assert abs(marks[1].cash-D('.6')) < D('1e-12')
    assert abs(marks[1].nav-D('60.3')) < D('1e-12')
    assert sum(e.fee for e in log) == D('.7')
    assert t == fixture(n)


@pytest.mark.parametrize('reverse',[False,True])
def test_priority_reversal_and_same_open_unavailable_proceeds(reverse):
    t=fixture(2)
    orders=(Order(CAL[0],CAL[1],'GA7:a','A','SELL',2),
            Order(CAL[0],CAL[1],'GA7:a','B','BUY',1),
            Order(CAL[0],CAL[1],'GA6:b','B','BUY',1))
    if reverse:
        orders=orders[:1]+tuple(reversed(orders[1:]))
    t=replace(t,cash=D(10),orders=orders)
    log=execute(t)
    assert [e.kind for e in log[:4]] == ['SETTLE','SELL','BUY','REJECT']
    assert log[2].owner == ('GA6:b' if reverse else 'GA7:a')
    same_events(log,reference(t)); same_events(log,funded(t))


@pytest.mark.parametrize('change',[
    {'session':CAL[4]}, {'observed':CAL[4]}, {'event_coverage':('A',)},
    {'corporate_actions':('dividend',)}, {'prices':(('A',D(10)),)},
])
def test_bad_late_coverage_fails_before_loading_native(monkeypatch,change):
    import discovery.competitive_ga.ga7_native_share_adapter as adapter
    def forbidden():
        raise AssertionError('native state constructed before whole-tape validation')
    monkeypatch.setattr(adapter,'load',forbidden)
    t=fixture()
    with pytest.raises(ValueError):
        execute(replace(t,opens=t.opens[:-1]+(replace(t.opens[-1],**change),)))


def test_native_source_hash_drift_rejected(monkeypatch,tmp_path):
    for name in kernels.HASHES:
        (tmp_path/name).write_bytes((kernels.ROOT/name).read_bytes())
    (tmp_path/'request_replay.py').write_text('# drift\n')
    monkeypatch.setattr(kernels,'ROOT',tmp_path)
    with pytest.raises(ValueError,match='unsupported native source'):
        execute(fixture())


def test_native_trade_account_methods_are_executed():
    scope,code=kernels.load()
    account=scope['TradeAccount']()
    account.buy(16.2,.02)
    p=scope['Position'](2,8.,16.2,0,8.,0,account=account)
    env=dict(scope,positions={'A':p},ticker='A',qty=1,price=10.,fee=.01,unsettled=[],i=1)
    exec(code['REDUCE'],env)
    assert p.shares == 1 and p.cost == 8.1
    assert account.open_cost == 8.1
    assert account.realized == pytest.approx(1.8)
    assert env['unsettled'] == [(2,9.9)]


def test_float_cash_boundary_explicitly_does_not_certify_decimal_contract():
    t=fixture(2)
    t=replace(t,cash=D('.3'),positions=(),receivables=(),fee_rate=D(0),
              orders=(Order(CAL[0],CAL[1],'a','A','BUY',3),),
              opens=tuple(Open(d,(('A',D('.1')),),d,('A',)) for d in CAL[1:3]))
    assert reference(t)[0].kind == funded(t)[0].kind == 'BUY'
    assert execute(t)[0].kind == 'REJECT'  # native float cost > float cash


def native_fixture():
    import sys
    sys.path.insert(0,str(kernels.ROOT.parent))
    from ga7.request_replay import replay_requests
    # Same explicit fixture genome pattern as existing native observer tests.
    from types import SimpleNamespace
    g=SimpleNamespace(identity=lambda:'fixture',feature_a='a',feature_b='b',
                      entry_pct=.1,stop_pct=.02,capacity=2,exit_rule='signal_decay')
    panels=[(CAL[i],{'A':dict(open=10.,close=10.,low=10.,features={'a':.6,'b':.6},eligible=True)},False) for i in range(4)]
    return replay_requests,g,panels


def test_actual_original_order_journal_and_trace_restoration():
    import sys
    from discovery.competitive_ga.ga7_native_journal import observe
    fn,g,panels=native_fixture()
    original,ledger=fn(g,panels,lambda g,b:True,cash_yield=0.,record_pass=True)
    observed,observed_ledger,orders,daily=observe(fn,g,panels,lambda g,b:True)
    assert original == observed and ledger.requests == observed_ledger.requests
    assert sys.gettrace() is None
    assert orders[0]['ticker'] == 'A'
    assert orders[0]['action'] == 'ENTER'
    assert orders[0]['filled_shares'] == 999
    assert orders[0]['fee'] == pytest.approx(9.99)
    assert orders[0]['after']['cash'] == pytest.approx(90000.01)
    assert daily[-1]['marked_nav'] == pytest.approx(99990.01)
    assert [o['action'] for o in orders] == ['ENTER','HOLD','HOLD']


def test_actual_trace_exception_and_existing_trace_restore():
    import sys
    from discovery.competitive_ga.ga7_native_journal import observe
    fn,g,panels=native_fixture()
    def boom(g,b):
        raise RuntimeError('fixture callback')
    with pytest.raises(RuntimeError):
        observe(fn,g,panels,boom)
    assert sys.gettrace() is None
    old=lambda *a:None
    sys.settrace(old)
    try:
        with pytest.raises(ValueError):
            observe(fn,g,panels,lambda g,b:True)
        assert sys.gettrace() is old
    finally:
        sys.settrace(None)


@pytest.mark.parametrize('rates',[(D(0),('13','9','15')),(D('.001'),('11','12','9'))])
def test_changing_opens_raw_basis_peak_and_independent_fee_math(rates):
    rate,prices=rates
    t=fixture()
    t=replace(t,fee_rate=rate,opens=tuple(replace(b,prices=(('A',D(p)),('B',D(10)))) for b,p in zip(t.opens,prices)))
    log=execute(t)
    same_events(log,reference(t)); same_events(log,funded(t))


@pytest.mark.parametrize('cash',[D('1e999'),D('1e-999')])
def test_native_float_range_fails_closed(cash):
    with pytest.raises(ValueError,match='native float range'):
        execute(replace(fixture(),cash=cash))


def test_actual_native_add_reduce_exit_journal():
    from discovery.competitive_ga.ga7_native_journal import observe
    fn,g,panels=native_fixture()
    panels.append((CAL[4],dict(panels[-1][1]),False))
    panels[1]=(CAL[1],{'A':dict(open=10.,close=10.5,low=10.,features={'a':.9,'b':.9},eligible=True)},False)
    panels[2]=(CAL[2],{'A':dict(open=11.,close=10.2,low=10.1,features={'a':.4,'b':.4},eligible=True)},False)
    panels[3]=(CAL[3],{'A':dict(open=10.,close=10.,low=10.,features={'a':.6,'b':.6},eligible=True)},True)
    observed,ledger,orders,daily=observe(fn,g,panels,lambda g,b:True)
    original,_=fn(g,panels,lambda g,b:True,cash_yield=0.,record_pass=True)
    assert observed == original
    fills=[o for o in orders if o['outcome']=='FILL']
    assert [(o['action'],o['filled_shares']) for o in fills] == [('ENTER',999),('INCREASE',275),('REDUCE',637),('EXIT',637)]
    assert not daily[-1]['state']['positions']
    assert fills[-1]['after']['receivables'][-1][0] == 5  # T+1 beyond last open


def test_native_account_add_partial_and_finish_dollar_oracle():
    scope,code=kernels.load()
    account=scope['TradeAccount']()
    account.buy(16.2,.02)
    p=scope['Position'](2,8.,16.2,0,8.,0,account=account)
    env=dict(scope,positions={'A':p},ticker='A',pos=p,qty=1,price=10.,fee=.01,
             unsettled=[],i=1,cash=100.,cash_flow=[])
    exec(code['ADD'],env)
    assert account.invested == pytest.approx(26.3)
    assert p.entry == pytest.approx(26/3)
    env.update(price=12.)
    exec(code['REDUCE'],env)
    assert p.shares == 2
    assert account.open_cost == pytest.approx(p.cost)
    env.update(price=9.)
    exec(code['EXIT'],env)
    # Net proceeds 11.88 + 17.82 minus all invested 26.30 = 3.40.
    assert env['ret'] == pytest.approx(3.4/26.3)
    assert env['actual_r'] == pytest.approx(3.4/(26.3*.02))
    assert not env['positions']


def test_mark_identity_hand_overnight_intraday_and_fees():
    from discovery.competitive_ga.phase9_diagnostics import components
    panels=[('d0',{'A':{'open':10.,'close':11.}},False),
            ('d1',{'A':{'open':12.,'close':13.}},False)]
    rows=components(panels,[{'A':2},{'A':3}],[.2,.3])
    assert rows[0]['nav_change'] == pytest.approx(1.8)
    assert rows[1]['overnight'] == 2
    assert rows[1]['intraday'] == 3
    assert rows[1]['nav_change'] == pytest.approx(4.7)


@pytest.mark.parametrize('cash,capacity',[(D(0),100),(D(1000),4)])
def test_isolated_cash_and_capacity_rejections(cash,capacity):
    t=replace(fixture(2),cash=cash,max_total_shares=capacity)
    log=execute(t)
    assert log[1].kind == 'REJECT'  # first ADD after opening settlement
    same_events(log,reference(t)); same_events(log,funded(t))
