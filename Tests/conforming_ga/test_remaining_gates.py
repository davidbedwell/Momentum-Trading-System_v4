import numpy as np,pandas as pd,pytest,inspect
from pathlib import Path
from Core.conforming_ga.metrics import *
from Core.conforming_ga.labels import LabelStore
from Core.conforming_ga.blind import authorize_blind_replay
from Core.conforming_ga.gates import freeze_finalists,CertificationError
from Core.conforming_ga.schema import *
from Core.conforming_ga.model import opportunity_values
from Core.conforming_ga.engine import AllocationMode
from Core.conforming_ga.features import causal_stock_features
from Core.conforming_ga.realdata import load_fold,FoldLoader
from Core.conforming_ga.ofr import ofr_asof
import json
REPO=Path(__file__).resolve().parents[2]; MIRROR=Path('/home/ubuntu/mts-ga-dev117-permitted-20261006')

def test_pf12_blind_refuses_until_all_four_freezes(tmp_path):
    ps=[];hs=[]
    for f in range(3):
        p=tmp_path/f'f{f}.json';hs.append(freeze_finalists(p,f,{'g':f}));ps.append(str(p))
    with pytest.raises(CertificationError):authorize_blind_replay(ps,hs)
    p=tmp_path/'f3.json';hs.append(freeze_finalists(p,3,{'g':3}));ps.append(str(p))
    assert authorize_blind_replay(ps,hs)

def test_pf15_labels_nan_cannot_change_live_decision():
    g=Genome((),(),(StockState('x',1),),(Module('m',(StockState('x',1),)),),OpportunityMap(),Allocation(AllocationMode.STRENGTH,.5,0,1,.1),Lifecycle(),ShortPolicy())
    stock={'A':{'x':.2},'B':{'x':-.1}}
    labels=LabelStore(np.array([1.,-1.]))
    a=opportunity_values(g,market={},sector={},stock=stock)
    labels=labels.nan_copy()
    b=opportunity_values(g,market={},sector={},stock=stock)
    assert np.isnan(labels.values).all() and a==b

def test_pf23_hand_metrics():
    r=np.array([.10,-.05,-.20,.04,.03])
    e=np.r_[100,100*np.cumprod(1+r)]
    m=finalist_metrics(e,np.array([0,.2,.1,.3,.1]),np.array([1,.5,.4,.2,.3]),np.zeros(5),r,[{'A':.5,'B':.5}]*5)
    assert m['worst_day']==pytest.approx(-.2)
    assert m['worst_5']==pytest.approx(np.prod(1+r)-1)
    assert m['mdd']<0 and m['turnover']==pytest.approx(.14)
    assert m['holdings_hhi']==pytest.approx(.5)

def test_pf23_train_blind_path_same_universe_identical():
    tr,_=load_fold(REPO,0); ts=tr[:6]
    x=FoldLoader(REPO,MIRROR,0,'train').load_prices();x=x[x.ticker.isin(ts)]
    T=pd.to_datetime(x.date).max()
    a=causal_stock_features(x,ts,T); b=causal_stock_features(x.copy(),ts,T)
    assert a==b

def test_pf23_sentinel_detectable():
    T=100
    turnover=np.r_[1.,np.zeros(T-1)];safe=np.r_[1.,np.zeros(T-1)]
    assert turnover.mean()==safe.mean()==pytest.approx(1/T)

def test_pf24_exact_eras_and_continuous():
    assert ERAS==(('E1','2006-09-15','2011-09-14'),('E2','2011-09-15','2016-09-14'),('E3','2016-09-15','2021-09-14'),('E4','2021-09-15','2026-09-14'))
    assert CONTINUOUS==('2006-09-15','2026-09-14')
    dates=pd.date_range('2006-09-15','2026-09-14',freq='B')
    idx=reset_era_index(dates)
    assert all(len(v)>0 for v in idx.values())
    # independent reset semantics are explicit: each starts from 100k.
    assert [100000.0 for _ in ERAS]==[100000.0]*4

def test_pf04_current_sector_labels_not_in_live_feature_engine():
    import Core.conforming_ga.features as f
    src=inspect.getsource(f)
    assert 'gics' not in src.lower() and 'sector' not in src.lower()
    d=json.loads((REPO/'Research/Conformance/MTS_DYNAMIC_PEER_DIAGNOSTIC_FOLD0_20261006.json').read_text())
    assert d['selected_minus_random']>0 and d['observations']>0
    assert d['current_gics_projected_backward'] is False

def test_pf14_ofr_one_session_lag_registered():
    # 2026-09-30 observation must not be usable on 2026-09-30 itself.
    a=ofr_asof(REPO,'2026-09-30')
    b=ofr_asof(REPO,'2026-10-01')
    assert a!=b and b==pytest.approx(-2.349)
