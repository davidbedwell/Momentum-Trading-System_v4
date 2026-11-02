import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
spec=importlib.util.spec_from_file_location('sequence',Path(__file__).with_name('study.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def fixture(n=20):
    f=pd.DataFrame(dict(dd=-.15,rv=.25,rv_change=-.01,b=.2,bmean=.2,ret5=.02,ema_slope=.01,above_count=5.,m63=-.1),index=pd.bdate_range('2020-01-01',periods=n))
    f.loc[f.index[2]:,['b','bmean']]=[.5,.5]
    return f

def test_strict_order_and_anchor():
    f=fixture();s,d,l=m.machine(f)
    assert d.state.iloc[:5].tolist()==[1,1,2,3,3]
    assert d.anchor_breadth.iloc[3]==.2
    row=d.iloc[3];assert row.damage_date<row.breadth_date<row.confirmation_date
    assert l.to_state.tolist()==[1,2,3]

def test_no_same_session_transition_even_if_all_gates_true():
    f=fixture();f.bmean=.5
    _,d,_=m.machine(f);assert d.state.iloc[0]==1 and d.state.iloc[2]==2 and d.state.iloc[3]==3

def test_deadline_inclusive_and_timeout():
    f=fixture();s,d,l=m.machine(f,wait_damage=2)
    assert d.state.iloc[2]==2
    f.loc[f.index[2],['b','bmean']]=.2
    s,d,l=m.machine(f,wait_damage=2)
    assert d.state.iloc[3]==0 and l.reason.iloc[-1]=='expiry'

def test_expiry_retention_rearm():
    f=fixture();_,d,l=m.machine(f,retention=2)
    assert d.state.iloc[3:6].tolist()==[3,3,0]
    f.loc[f.index[6]:,['dd','b','bmean']]=[-.15,.2,.2]
    _,d,l=m.machine(f,retention=2)
    assert (d.state.iloc[6:]==0).all()  # no idle false gate between episodes
    f.loc[f.index[6],'dd']=0
    _,d,l=m.machine(f,retention=2)
    assert d.state.iloc[7]==1

def test_missing_aborts_does_not_confirm():
    f=fixture();f.loc[f.index[3],'rv']=np.nan
    s,d,l=m.machine(f)
    assert np.isnan(d.state.iloc[3]) and s.iloc[3].isna().all()
    assert not s.confirmed.eq(1).any()
    assert 'missing_abort' in l.reason.tolist()

def test_prefix_invariance_and_future_perturbation():
    f=fixture(100);a=m.machine(f)
    for n in [1,3,4,10,60]:
        b=m.machine(f.iloc[:n]);pd.testing.assert_frame_equal(a[0].iloc[:n],b[0]);pd.testing.assert_frame_equal(a[1].iloc[:n],b[1])
    f.iloc[50:]=0
    pd.testing.assert_frame_equal(a[0].iloc[:50],m.machine(f)[0].iloc[:50])

def test_features_causal_and_missing_prices():
    rng=np.random.default_rng(5);idx=pd.bdate_range('2005-01-01',periods=500)
    p=pd.Series(100*np.exp(np.cumsum(rng.normal(0,.01,500))),index=idx)
    x=pd.DataFrame({str(i):p*(1+i*.01) for i in range(25)})
    full=m.features(p,x);short=m.features(p.iloc[:400],x.iloc[:400])
    pd.testing.assert_frame_equal(full.iloc[:400],short)
    p2=p.copy();x2=x.copy();p2.iloc[400:]*=2;x2.iloc[400:]*=3
    pd.testing.assert_frame_equal(full.iloc[:400],m.features(p2,x2).iloc[:400])
    x.iloc[300,:]=np.nan;assert np.isnan(m.features(p,x).b.iloc[300])

def test_outcomes_and_year_purging():
    p=pd.Series([100.,120.,90.,110.],index=pd.bdate_range('2020-01-01',periods=4))
    y=m.prior.outcomes(p,3);assert np.isclose(y['return'].iloc[0],.1) and np.isclose(y.drawdown.iloc[0],-.25)
    idx=pd.bdate_range('2019-10-01','2021-04-01');ok=m.period(idx,63)
    ep=pd.Series(idx).shift(-63)
    assert (ep[ok].dt.year.to_numpy()==idx[ok].year).all()
    assert not m.period(idx,21,omit=[2020])[idx.year==2020].any()

def test_matching_support_weights_and_paired_inference():
    a=np.array([1,1,0,0,0,1],bool);b=np.array([0,0,1,1,1,0],bool);k=['x','x','x','x','y','z']
    aa,w=m.match(a,b,k);assert aa.sum()==2 and w.tolist()==[0,0,1,1,0,0]
    assert w.sum()==aa.sum()
    rng=np.random.default_rng(9);y=rng.normal(size=500);a=np.arange(500)%3==0;b=np.arange(500)%2==0
    np.testing.assert_allclose(m.weighted_estimate(y,a,b.astype(float),63),m.prior.estimate(y,a,b,63))
    same=m.weighted_estimate(y,a,a.astype(float),63);assert same[0]==0 and same[3]==0

def test_multiple_comparisons_and_delayed_states():
    d=m.adjust(pd.DataFrame({'p':[.01,.04,np.nan]}));np.testing.assert_allclose(d.q.iloc[:2],[.02,.04]);assert d.bonferroni.iloc[0]==.02
    s,_,_=m.machine(fixture());assert s.shift(1).confirmed.iloc[4]==s.confirmed.iloc[3]

def test_hard_episode_cap():
    f=fixture(200);f.loc[f.index[:110],['b','bmean']]=.2
    _,d,l=m.machine(f,wait_damage=120,wait_breadth=120,retention=100)
    assert d.state.iloc[126]==3 and d.state.iloc[127]==0

def test_breadth_timeout_requires_later_price_confirmation():
    f=fixture();f.above_count=0
    _,d,l=m.machine(f,wait_breadth=2)
    assert d.state.iloc[4]==2 and d.state.iloc[5]==0
    assert not d.state.eq(3).any()

def test_identical_arm_is_not_significant_for_real_scale():
    rng=np.random.default_rng(1);y=rng.normal(0,.08,5000);a=np.arange(5000)%13==0
    e=m.weighted_estimate(y,a,a.astype(float),126)
    assert e[:4]==(0.,0.,0.,0.) and np.isnan(e[4])
