import pytest
from discovery.competitive_ga.fold_trade_reconstruction import FoldTrade,reconstruct
from discovery.competitive_ga.causal_scaling_evidence import EvidenceBook

def make(trades):
    return reconstruct('GA7','c7','f1',0,10,11,trades,'ledger-sha-1')

def test_reconstruction_compounds_matured_net_trades():
    fold=make([FoldTrade('a',1,3,.20,'shadow'),FoldTrade('b',4,8,-.10,'shadow')])
    assert fold.trades==2
    assert fold.net_return==pytest.approx(.08)
    assert fold.drawdown==pytest.approx(.10)
    book=EvidenceBook();book.add(fold)
    assert book.estimate('GA7','c7',11) is None
    assert book.estimate('GA7','c7',12).matured_trades==2

def test_reconstruction_rejects_unmatured_and_duplicate_trades():
    with pytest.raises(ValueError,match='outside fold'):
        make([FoldTrade('a',2,11,.1,'shadow')])
    with pytest.raises(ValueError,match='duplicate'):
        make([FoldTrade('a',1,3,.1,'shadow'),FoldTrade('a',4,5,.1,'shadow')])

def test_reconstruction_rejects_mixed_sources_and_invalid_returns():
    with pytest.raises(ValueError,match='mixed'):
        make([FoldTrade('a',1,3,.1,'shadow'),FoldTrade('b',4,5,.1,'actual')])
    with pytest.raises(ValueError,match='invalid net return'):
        make([FoldTrade('a',1,3,-1.,'shadow')])
