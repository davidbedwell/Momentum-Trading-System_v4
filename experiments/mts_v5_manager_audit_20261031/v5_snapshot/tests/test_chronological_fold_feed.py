import pytest
from discovery.competitive_ga.chronological_fold_feed import FoldBatch,schedule
from discovery.competitive_ga.fold_trade_reconstruction import FoldTrade
from discovery.competitive_ga.causal_scaling_evidence import EvidenceBook

def test_schedule_only_exposes_completed_trade_folds():
    batch=FoldBatch('GA7','c7','f1',0,9,10,'audited-ledger',(
        FoldTrade('a',1,3,.1,'shadow'),FoldTrade('b',4,8,-.02,'shadow')))
    feed=schedule([batch]);assert set(feed)=={10}
    book=EvidenceBook();book.add(feed[10][0])
    assert book.estimate('GA7','c7',10) is None
    assert book.estimate('GA7','c7',11).matured_trades==2

def test_feed_rejects_unfinished_trade():
    batch=FoldBatch('GA7','c7','f1',0,9,10,'audited-ledger',(
        FoldTrade('a',1,10,.1,'shadow'),))
    with pytest.raises(ValueError,match='outside fold'):schedule([batch])
