import pytest
from discovery.competitive_ga.position_fill_book import FillBook

def test_entry_add_partial_exit_and_full_exit():
    b=FillBook()
    b.apply(('d1','A','BUY',10,100,1),('GA7','c1'),.02)
    assert b.held('A',105,10000)['entry']==pytest.approx(100.)
    b.apply(('d2','A','BUY',10,110,1),('GA7','c1'))
    assert b.held('A',110,10000)['entry']==pytest.approx(105.)
    b.apply(('d3','A','SELL',5,120,.5),('GA7','c1'))
    assert b.positions['A'].shares==15
    assert b.realized[0]['pnl']==pytest.approx(74.)
    b.apply(('d4','A','SELL',15,90,1.5),('GA7','c1'))
    assert 'A' not in b.positions
    assert b.realized[-1]['pnl']==pytest.approx(-228.)

def test_owner_protection():
    b=FillBook()
    b.apply(('d1','A','BUY',10,100,1),('GA7','c1'),.02)
    with pytest.raises(ValueError,match='cross-owner'):
        b.apply(('d2','A','BUY',1,101,.1),('GA6','c2'))
    with pytest.raises(ValueError,match='cross-owner'):
        b.apply(('d3','A','SELL',1,101,.1),('GA6','c2'))

def test_missing_stop_and_oversell():
    b=FillBook()
    with pytest.raises(ValueError,match='missing stop'):
        b.apply(('d1','A','BUY',1,100,.1),('GA7','c1'))
    b.apply(('d1','A','BUY',1,100,.1),('GA7','c1'),.02)
    with pytest.raises(ValueError,match='unowned sell'):
        b.apply(('d2','A','SELL',2,100,.1))
