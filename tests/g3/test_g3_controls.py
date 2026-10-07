import numpy as np,pytest
from Core.g3.controls import *

def test_null_family_dispatch_and_n2_barrier():
    y=np.arange(300*2,dtype=float).reshape(300,2)
    assert not np.array_equal(apply_single_ticker_null(y,"N1_TEMPORAL_BLOCK",1),y)
    assert not np.array_equal(apply_single_ticker_null(y,"N3_GUARDED_SHIFT",1),y)
    with pytest.raises(ValueError): apply_single_ticker_null(y,"N2_DATEWISE_CROSS_SECTION",1)

def test_n2_aligned_cross_section_preserves_each_date_values():
    y=np.arange(20*4,dtype=float).reshape(20,4,1)
    z=apply_aligned_n2(y,7)
    for d in range(20): assert sorted(z[d,:,0])==sorted(y[d,:,0])

def test_search_ledger_counts_all_attempts():
    l=SearchLedger()
    l.add(SearchAttempt("r1","real",None,6,48,8,2304,1,True))
    l.add(SearchAttempt("r1","null","N1_TEMPORAL_BLOCK",6,48,8,2304,1,True))
    assert l.total_ticker_evaluations==4608 and l.reviewed_attempts==2
    with pytest.raises(ValueError): l.add(SearchAttempt("r1","real",None,1,1,1,1,1,False))

def test_validation_barrier_requires_exact_frozen_genome_and_scope():
    g={"a":1};s={"tickers":["A","B"],"dates":["2020","2021"]}
    c=freeze_candidate("c1",g,s,"r1")
    assert_validation_barrier(c,g,s,True)
    with pytest.raises(ValueError): assert_validation_barrier(c,{"a":2},s,True)
    with pytest.raises(ValueError): assert_validation_barrier(c,g,{"tickers":["A"]},True)
    with pytest.raises(ValueError): assert_validation_barrier(c,g,s,False)
