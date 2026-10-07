import numpy as np,pytest
from Core.g3.preregistered_nullgate import *

def rows(a):
    return sorted(map(tuple,np.asarray(a).tolist()))

def test_nb_preserves_y_rows_exactly_and_changes_alignment():
    y=np.arange(2500*3,dtype=float).reshape(2500,3);x=np.arange(2500*2,dtype=float).reshape(2500,2)
    xx,yy=apply_frozen_null(x,y,NULL_B,11)
    assert np.array_equal(xx,x)
    assert rows(yy)==rows(y)
    assert not np.array_equal(yy,y)

def test_nc_preserves_multivariate_x_rows_and_y_exactly():
    x=np.arange(2500*4,dtype=float).reshape(2500,4);y=np.arange(2500*2,dtype=float).reshape(2500,2)
    xx,yy=apply_frozen_null(x,y,NULL_C,12)
    assert rows(xx)==rows(x)
    assert np.array_equal(yy,y)
    assert not np.array_equal(xx,x)

def test_na_is_same_stock_contiguous_block_resample_and_frozen_length():
    y=np.arange(2500,dtype=float)[:,None];x=np.zeros((2500,2))
    _,z=apply_frozen_null(x,y,NULL_A,13)
    assert len(z)==2500
    # ceil(sqrt(2500))=50: every interior step inside each output block is +1.
    dz=np.diff(z[:,0])
    boundary=np.arange(49,2499,50)
    mask=np.ones(len(dz),bool);mask[boundary]=False
    assert np.all(dz[mask]==1)

def test_guard_is_quarter_to_three_quarter_panel():
    a=np.arange(2500)[:,None]
    z=guarded_shift_rows(a,99)
    shift=int(np.flatnonzero(z[:,0]==0)[0])
    # np.roll by s places original row 0 at index s.
    assert 625 <= shift <= 1875

def test_gate_requires_25_paired_replicates_and_two_of_three():
    real=np.ones(25)
    nulls={NULL_A:np.zeros(25),NULL_B:np.zeros(25),NULL_C:np.ones(25)*2}
    d=evaluate_replicated_gate(real,nulls)
    assert d.significant_nulls==2 and d.state=="PASS_2_OF_3"
    with pytest.raises(ValueError): evaluate_replicated_gate(real[:-1],nulls)

def test_gate_all_equal_is_fail():
    real=np.ones(25);nulls={k:np.ones(25) for k in FROZEN_NULL_FAMILIES}
    d=evaluate_replicated_gate(real,nulls)
    assert d.significant_nulls==0 and d.state=="FAIL_NO_LARGE_DISCOVERY"
