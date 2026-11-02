import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
spec=importlib.util.spec_from_file_location('followup',Path(__file__).with_name('study.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def sample():
    rng=np.random.default_rng(19);idx=pd.bdate_range('2010-01-01',periods=850)
    p=pd.Series(100*np.exp(np.cumsum(rng.normal(.0003,.015,len(idx)))),index=idx)
    x=pd.DataFrame(100*np.exp(np.cumsum(rng.normal(.0003,.022,(len(idx),30)),axis=0)),index=idx)
    return p,x

def test_future_perturbation_and_prefix():
    p,x=sample();f,s,c=m.build(p,x);cut=600
    p2=p.copy();x2=x.copy();p2.iloc[cut:]*=3;x2.iloc[cut:]*=.1
    f2,s2,_=m.build(p2,x2)
    pd.testing.assert_frame_equal(f.iloc[:cut],f2.iloc[:cut]);pd.testing.assert_frame_equal(s.iloc[:cut],s2.iloc[:cut])
    ft,st,_=m.build(p.iloc[:cut],x.iloc[:cut]);pd.testing.assert_frame_equal(ft,f.iloc[:cut]);pd.testing.assert_frame_equal(st,s.iloc[:cut])
    assert len(c)==28

def test_missing_and_conjunction():
    p,x=sample();x.iloc[400:460]=np.nan
    f,s,c=m.build(p,x)
    assert s.weak.iloc[400:460].isna().all()
    for rule,parts in c.items():
      if len(parts)>1:
        ok=s[parts].notna().all(axis=1)
        pd.testing.assert_series_equal(s.loc[ok,rule].astype(bool),s.loc[ok,parts].eq(1).all(axis=1),check_names=False)
        assert s.loc[~ok,rule].isna().all()

def test_labels_and_purging():
    idx=pd.bdate_range('2011-01-01',periods=800)
    p=pd.Series(np.resize([100.,120.,90.,110.,130.,105.],len(idx)),index=idx)
    y=m.prior.outcomes(p,5)
    assert np.isclose(y['return'].iloc[0],.05)
    assert np.isclose(y.drawdown.iloc[0],-.25)
    assert y.iloc[-5:].isna().all().all()
    for h in m.H:
      ok=m.period(idx,h);ep=pd.Series(idx).shift(-h)
      assert (ep[ok].dt.year.to_numpy()==idx[ok].year).all()
      assert (idx[ok].year>=2012).all()

def test_inference_overlap_and_counts():
    y=np.arange(100,dtype=float);a=np.arange(100)%2==0
    e=m.prior.estimate(y,a,a)
    assert np.allclose(e[:4],0)
    assert m.prior.counts(np.ones(100,dtype=bool),21)==(1,5)
    assert np.allclose(m.prior.bh([.01,.04,.03]),[.03,.04,.04])

def test_executed_outputs_consistent():
    root=Path(__file__).parent
    if not (root/'results.csv').exists():return
    r=pd.read_csv(root/'results.csv');roll=pd.read_csv(root/'rolling_results.csv')
    selections=pd.read_csv(root/'rolling_selections.csv')
    assert selections.year.tolist()==list(range(2012,2026))
    assert (selections.training_n>=100).all() and (selections.training_onsets>=15).all()
    assert set(selections.rule)=={'weak&stabilization'}
    a=r.query("rule=='weak&stabilization' and comparator in ['unconditional','momentum']").sort_values(['comparator','horizon','metric'])
    b=roll.sort_values(['comparator','horizon','metric'])
    for col in ['n','mean','effect','ci_low','ci_high']:
        assert np.allclose(a[col],b[col],equal_nan=True)
    assert r.q.dropna().between(0,1).all()
    assert len(pd.read_csv(root/'interactions.csv'))==15*4*3
