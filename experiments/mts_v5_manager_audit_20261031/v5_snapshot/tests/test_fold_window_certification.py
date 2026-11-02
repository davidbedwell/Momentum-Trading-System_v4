import pytest
from discovery.competitive_ga.causal_scaling_evidence import EvidenceBook,FoldRecord

def record(name,start,end,maturity,independent=True,provenance=None):
    return FoldRecord('GA7','c7',name,0,maturity,.1,.1,40,'shadow',independent,start,end,provenance or name)

def test_overlapping_validation_folds_rejected():
    b=EvidenceBook();b.add(record('a',1,5,7))
    with pytest.raises(ValueError,match='overlapping'):
        b.add(record('b',5,9,11))

def test_reused_provenance_rejected():
    b=EvidenceBook();b.add(record('a',1,3,5,provenance='same'))
    with pytest.raises(ValueError,match='reused'):
        b.add(record('b',6,8,10,provenance='same'))

def test_independence_requires_boundaries():
    b=EvidenceBook()
    with pytest.raises(ValueError,match='boundaries'):
        b.add(record('a',-1,-1,6))
    with pytest.raises(ValueError,match='causal provenance'):
        b.add(record('b',1,6,6))

def test_family_isolation_and_disjoint_windows():
    b=EvidenceBook();b.add(record('a',1,3,5));b.add(record('b',4,6,8))
    b.add(FoldRecord('GA6','c7','a',0,5,.1,.1,40,'shadow',True,1,3,'a'))
    assert b.estimate('GA7','c7',9).forward_folds==2
    assert b.estimate('GA6','c7',9).forward_folds==1
