import pytest
from discovery.competitive_ga.causal_scaling_evidence import EvidenceBook, FoldRecord
from discovery.competitive_ga.progressive_scaling import allowed_target

def fold(i, independent=True):
    return FoldRecord('GA7','c7',str(i),i*10,i*10+5,.08,.10,40,'shadow',independent,i*10+1,i*10+4,'ledger-'+str(i))

def test_strict_maturity_and_three_independent_folds():
    b=EvidenceBook()
    for i in range(3): b.add(fold(i))
    assert b.estimate('GA7','c7',5) is None
    assert b.estimate('GA7','c7',15).matured_trades==40
    ev=b.estimate('GA7','c7',26,True,True)
    assert ev.matured_trades==120 and ev.forward_folds==3
    assert allowed_target(.07,.30,ev,stop_distance=.02,gap_risk=.03)==pytest.approx(.30)

def test_duplicate_and_invalid_fold_rejected():
    b=EvidenceBook();b.add(fold(0))
    with pytest.raises(ValueError,match='duplicate'):b.add(fold(0))
    with pytest.raises(ValueError,match='chronology'):b.add(FoldRecord('GA7','c7','bad',4,4,.1,.1,1,'shadow',True))

def test_nonindependent_folds_cannot_unlock_thirty_percent():
    b=EvidenceBook()
    for i in range(3):b.add(fold(i,independent=i!=2))
    ev=b.estimate('GA7','c7',26,True,True)
    assert not ev.independent_confirmation
    assert allowed_target(.07,.30,ev,stop_distance=.02,gap_risk=.03)==pytest.approx(.20)
