import pytest
from discovery.competitive_ga.native_daily_replay_adapter import daily_producer
from discovery.competitive_ga.position_fill_book import FillBook
from engines.portfolio_replay.kernel import Bar

DATE='2026-01-12'

def test_adapter_supplies_executed_held_state():
    book=FillBook()
    book.apply((DATE,'AAA','BUY',10,100,1),('GA7','g7'),stop=.02)
    seen=[]
    def ga6(date,held,defensive):
        seen.append(held['AAA'])
        return []
    native=daily_producer({DATE:dict(trained_through='2026-01-11',
        source_hash='s',snapshot_hash='h',ga6_producer=ga6)})
    assert native(DATE,0,{'AAA':Bar(100,101)}, {'AAA':.1},
        {'AAA':('GA7','g7')},False,book)==()
    assert seen[0]['entry']==100.0 and seen[0]['weight']==.1
    assert seen[0]['owner']==('GA7','g7')

def test_missing_date_is_rejected():
    with pytest.raises(ValueError,match='missing dated'):
        daily_producer({})(DATE,0,{}, {},{},False,FillBook())
