import importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
spec=importlib.util.spec_from_file_location('study',Path(__file__).with_name('study.py'))
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_prefix_invariance_and_future_perturbation():
    rng=np.random.default_rng(42);idx=pd.bdate_range('2004-01-01',periods=700)
    p=pd.Series(100*np.exp(np.cumsum(rng.normal(0,.01,700))),index=idx)
    x=pd.DataFrame({str(i):p*np.exp(np.cumsum(rng.normal(0,.005,700))) for i in range(25)})
    full=m.features(p,{'DEV79':x});prefix=m.features(p.iloc[:500],{'DEV79':x.iloc[:500]})
    pd.testing.assert_frame_equal(full.iloc[:500],prefix)
    p2=p.copy();p2.iloc[500:]*=3;x2=x.copy();x2.iloc[500:]*=.1
    altered=m.features(p2,{'DEV79':x2})
    pd.testing.assert_frame_equal(full.iloc[:500],altered.iloc[:500])
    pd.testing.assert_frame_equal(m.rules(full).iloc[:500],m.rules(altered).iloc[:500])

def test_forward_drawdown_and_censoring():
    p=pd.Series([100.,120.,90.,110.,130.],index=pd.bdate_range('2020-01-01',periods=5))
    y=m.outcomes(p,2)
    assert np.isclose(y['return'].iloc[0],-.1)
    assert np.isclose(y.drawdown.iloc[0],-.25)
    assert np.isclose(y.adverse.iloc[0],-.1)
    assert y.downside.iloc[0]==1
    assert y.iloc[-2:].isna().all().all()

def test_missing_breadth_never_becomes_weak():
    idx=pd.bdate_range('2005-01-01',periods=250);p=pd.Series(np.arange(250)+100.,index=idx)
    x=pd.DataFrame({str(i):p for i in range(20)});x.iloc[220,0]=np.nan
    f=m.features(p,{'DEV79':x});s=m.rules(f)
    assert f.DEV79_b50.iloc[219]==1
    assert np.isnan(f.DEV79_b50.iloc[220])
    assert np.isnan(s.DEV79_breadth50_weak.iloc[220])
    assert np.isnan(f.DEV79_b200.iloc[198])

def test_hac_paired_zero_and_bh():
    y=np.arange(200.)/100;mask=np.arange(200)%2==0
    assert m.estimate(y,mask,mask)[:4]==(0.,0.,0.,0.)
    q=m.bh([.01,.04,.03,np.nan]);np.testing.assert_allclose(q[:3],[.03,.04,.04]);assert np.isnan(q[3])
    assert m.counts([1,1,0,1,1,1],3)==(2,2)

def test_split_endpoints_and_output_integrity():
    root=Path(__file__).parent
    if not (root/'outcomes.csv').exists():return
    outcomes=pd.read_csv(root/'outcomes.csv',header=[0,1],index_col=0)
    signals=pd.read_csv(root/'signals.csv',index_col=0,parse_dates=True)
    result=pd.read_csv(root/'results.csv')
    idx=signals.index
    for split,start,end in [('discovery','2006-01-01','2016-12-31'),('validation','2017-01-01','2025-12-31')]:
        for h in m.HORIZONS:
            endpoint=pd.Series(idx,index=idx).shift(-h)
            eligible=(idx>=start)&(idx<=end)&(endpoint<=end).to_numpy()&signals.momentum63_positive.notna().to_numpy()
            a=eligible&(signals.momentum63_positive.to_numpy()==1)
            row=result.query("split==@split and horizon==@h and rule=='momentum63_positive' and metric=='return' and comparator=='unconditional'").iloc[0]
            assert row.n==a.sum()
            assert row.baseline_n==eligible.sum()
            assert np.isclose(row['mean'],outcomes[(str(h),'return')].to_numpy()[a].mean())
    assert result.q.dropna().between(0,1).all()
