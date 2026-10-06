import numpy as np,pytest
from Core.conforming_ga.evidence import *

def test_effective_n_iid_near_n():
    rng=np.random.default_rng(5);x=rng.normal(size=2000)
    n=newey_west_effective_n(x,5)
    assert 1500<n<2600

def test_effective_stocks_hand_calc():
    assert effective_stocks([1,1,0,0])==pytest.approx(2)

def test_effective_bets_independent_columns():
    rng=np.random.default_rng(7);x=rng.normal(size=(5000,3))
    assert 2.8<effective_bets(x)<=3.01

def test_cross_era_and_transport():
    r=cross_era_recurrence([1,-1,2,3]);assert r['positive_eras']==3 and r['negative_eras']==1
    assert cross_stock_transport(1,1.5)['delta']==pytest.approx(.5)

def test_trial_multiplicity_exact():
    assert trial_multiplicity([[1,2],[1,2],[2,3]])==2

def test_full_evidence_has_required_surfaces():
    r=np.array([.01,-.02,.03,-.01,.005]);e=np.r_[100,100*np.cumprod(1+r)]
    z=full_evidence(session_returns=r,equity=e,turnover=np.ones(5)*.1,safe_weight=np.ones(5)*.5,
      short_share=np.zeros(5),weights_by_session=[{'A':.5}]*5,stock_sessions=50,trades=3,
      pnl_by_stock=[1,2],holding_returns=np.random.default_rng(1).normal(size=(20,2)),
      sector_pnl={'x':1},episode_records=[{}],era_contributions=[1,2,3,4],
      train_metric=.1,blind_metric=.08,behavior_matrix=[[1,2],[2,3]])
    for k in ('raw_n','effective_n_sessions_newey_west','effective_stocks','effective_bets','sectors_contributing_nonzero','episodes','cross_era_recurrence','cross_stock_transport','trial_multiplicity_exact_behavioral','diagnostics'):
        assert k in z
