import numpy as np
from Core.g3.v3_protocol import V3Specialist, stationary_bootstrap_y, evaluate_v3
from Core.g3.starter import Rule

def test_stationary_bootstrap_deterministic_and_shape():
    y=np.arange(1000).reshape(100,10)
    a=stationary_bootstrap_y(y,123,50); b=stationary_bootstrap_y(y,123,50)
    assert a.shape==y.shape and np.array_equal(a,b) and not np.array_equal(a,y)

def test_applicability_is_hard_entry_condition():
    x=np.zeros((100,3)); y=np.full((100,10),.001)
    x[:20,0]=2; x[:,1]=2; x[:,2]=2
    g=V3Specialist(Rule(0,1,1),Rule(1,1,1),Rule(2,1,1),1,.2,.2,5,.1,.1)
    out=evaluate_v3(g,x,y,10)
    assert len(out)==20

def test_no_ticker_identity_field():
    assert "ticker" not in V3Specialist.__dataclass_fields__
    assert "sector" not in V3Specialist.__dataclass_fields__
