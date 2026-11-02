from dataclasses import replace
from decimal import Decimal as D
import pytest
from discovery.competitive_ga.share_order_contract import Tape, Open, Order, Position, Receivable
from discovery.competitive_ga.native_style_share_executor import execute as native
from discovery.competitive_ga.funded_share_executor import execute as shadow

CAL = ('2023-01-02','2023-01-03','2023-01-04','2023-01-05','2023-01-06')

def tape():
    orders = (
        Order(CAL[0],CAL[1],'GA6:a','A','BUY',4),
        Order(CAL[0],CAL[1],'GA7:b','A','BUY',2),
        Order(CAL[1],CAL[2],'GA6:a','A','BUY',1),
        Order(CAL[1],CAL[2],'GA6:a','A','SELL',2),
        Order(CAL[2],CAL[3],'GA6:a','A','SELL',3),
        Order(CAL[2],CAL[3],'GA7:b','A','SELL',2),
    )
    return Tape('fixed-shares-v1',CAL,D(100),(),(),orders,
                tuple(Open(day,(('A',D(10)),),day,('A',)) for day in CAL[1:4]),D('.01'),'T+1',100)

@pytest.mark.parametrize('engine',[native,shadow])
def test_hand_cash_fee_add_reduce_exit_and_owners(engine):
    t = tape()
    log = engine(t)
    marks = [e for e in log if e.kind == 'MARK']
    assert [m.cash for m in marks] == [D('39.4'),D('29.3'),D('49.1')]
    assert [m.nav for m in marks] == [D('99.4'),D('99.1'),D('98.6')]
    assert sum(r.amount for r in marks[-1].receivables) == D('49.5')
    assert marks[-1].positions == ()
    assert marks[1].positions[0] == Position('GA6:a','A',3,D(10),D('10.1'),2,D(10))
    assert sum(e.fee for e in log) == D('1.4')
    assert t == tape()  # no caller mutation
    assert all(e.cash >= 0 for e in log)
    assert log == shadow(t) == native(t)

@pytest.mark.parametrize('engine',[native,shadow])
def test_capacity_cash_and_inventory_are_all_or_none_and_priority(engine):
    t = tape()
    t = replace(t,max_total_shares=5,orders=t.orders[:2])
    first = engine(t)
    assert [e.kind for e in first[:2]] == ['BUY','REJECT']
    assert first[1].positions == first[0].positions
    reversed_log = engine(replace(t,orders=tuple(reversed(t.orders))))
    assert reversed_log[0].owner == 'GA7:b'
    assert reversed_log[1].kind == 'REJECT'
    assert engine(replace(t,cash=D(1)))[0].kind == 'REJECT'
    sell = replace(t.orders[0],side='SELL',shares=1)
    assert engine(replace(t,orders=(sell,)))[0].kind == 'REJECT'

@pytest.mark.parametrize('engine',[native,shadow])
def test_nonempty_state_due_credit_no_same_open_sale_funding(engine):
    t = tape()
    p = Position('GA6:a','A',2,D(8),D('8.1'),7,D(12))
    orders = (replace(t.orders[0],side='SELL',shares=2),replace(t.orders[1],shares=2))
    t = replace(t,cash=D(0),positions=(p,),receivables=(Receivable(CAL[1],D(1),'GA6:a'),),orders=orders)
    log = engine(t)
    assert [e.kind for e in log[:3]] == ['SETTLE','SELL','REJECT']
    assert log[2].cash == D(1)
    assert [e for e in log if e.kind == 'MARK'][1].cash == D('20.8')
    assert log == native(t) == shadow(t)

BAD = [
    {'version':'v2'}, {'cash':D(-1)}, {'cash':D('NaN')}, {'fee_rate':D(1)},
    {'settlement':'T+0'}, {'max_total_shares':True}, {'calendar':tuple(reversed(CAL))},
    {'positions':(Position('', 'A',1,D(10),D(10),0,D(10)),)},
    {'positions':(Position('x','A',1,D(10),D(9),0,D(10)),)},
    {'receivables':(Receivable(CAL[0],D(1),'x'),)},
]
@pytest.mark.parametrize('change',BAD)
@pytest.mark.parametrize('engine',[native,shadow])
def test_invalid_contract_rejected(change,engine):
    with pytest.raises(ValueError):
        engine(replace(tape(),**change))

@pytest.mark.parametrize('change',[{'shares':1.5},{'shares':True},{'shares':0},{'side':'HOLD'},
                                    {'owner':''},{'decision':CAL[1]},{'execution':CAL[4]}])
@pytest.mark.parametrize('engine',[native,shadow])
def test_invalid_orders(change,engine):
    t=tape()
    with pytest.raises(ValueError):
        engine(replace(t,orders=(replace(t.orders[0],**change),)))

@pytest.mark.parametrize('change',[{'prices':()},{'prices':(('A',D('Infinity')), )},
    {'event_coverage':()},{'corporate_actions':('split',)},{'observed':CAL[4]}])
@pytest.mark.parametrize('engine',[native,shadow])
def test_entire_tape_prevalidated_including_late_events(change,engine):
    t=tape()
    with pytest.raises(ValueError):
        engine(replace(t,opens=t.opens[:-1]+(replace(t.opens[-1],**change),)))

@pytest.mark.parametrize('engine',[native,shadow])
def test_different_open_price_basis_peak_and_cash_conservation(engine):
    t=tape()
    bars=tuple(replace(b,prices=(('A',D(p)),)) for b,p in zip(t.opens,(10,12,9)))
    log=engine(replace(t,opens=bars))
    cashflows=D(100)
    for e in log:
        if e.kind=='BUY': cashflows-=e.price*e.shares+e.fee
        if e.kind=='SELL': cashflows+=e.price*e.shares-e.fee
        if e.kind=='MARK':
            assert e.cash+sum((r.amount for r in e.receivables),D(0))==cashflows
    assert log == native(replace(t,opens=bars)) == shadow(replace(t,opens=bars))
