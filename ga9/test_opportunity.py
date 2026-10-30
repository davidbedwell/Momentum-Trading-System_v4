"""Causal boundary and allocator integration regressions for GA9-A."""
from dataclasses import replace
import numpy as np
import pandas as pd
from .manager_pilot import fixture
from .opportunity import discovery, outcomes, fit, Strategy, arrays, allocate


def panel():
    p,_=fixture()
    p.screen_score,p.screen_mask=discovery(p.close,p.eligible,4)
    return p


def test_discovery_is_daily_pit_and_prefix_invariant():
    p=panel();eligible=p.eligible.copy();eligible[150:,0]=False
    a,b=discovery(p.close,eligible,4)
    assert not b[150:,0].any()
    assert b.sum(axis=1).max()==4
    c=p.close.copy();c[400:]*=10
    _,changed=discovery(c,eligible,4)
    np.testing.assert_array_equal(b[:400],changed[:400])


def test_only_matured_labels_and_models_ignore_future():
    p=panel();s=Strategy(horizon=20)
    y,_=outcomes(p,20,756)
    assert np.isnan(y[735:]).all()
    assert np.isfinite(y[734]).all()
    m=fit(p,s)
    close=p.close.copy();opens=p.open.copy();close[756:]*=20;opens[756:]*=30
    changed=replace(p,close=close,open=opens)
    assert fit(changed,s)==m
    z=allocate(p,m,1008,1050)
    date_to_i={str(d.date()):i for i,d in enumerate(p.dates)}
    for f in z['fills']:
        assert date_to_i[f['date']]==date_to_i[f['decision_date']]+1
    assert z['audit']['max_identity_error']<1e-5


def test_unsupported_forecasts_abstain():
    p=panel();m=fit(p,Strategy())
    for row in m['bins']:row['supported']=False
    signal,hold=arrays(p,m)
    assert np.isneginf(signal).all()
    assert np.isnan(hold).all()
    assert allocate(p,m,1008,1050)['metrics']['fills']==0


def test_policy_labels_execute_stop_at_following_open_with_gap():
    from .opportunity import strategy_outcomes, ENTRY, EXIT
    p=panel(); c=np.full_like(p.close,100.);o=c.copy()
    c[1]=97.;o[2]=80.
    changed=replace(p,close=c,open=o)
    y,d=strategy_outcomes(changed,Strategy(horizon=5),10)
    # All units stop after first held close; next-open gap and both costs count.
    np.testing.assert_allclose(y[0],(2/3)*80*EXIT/(100*ENTRY)+1/3-1)
    assert (d[0]<=y[0]+1e-12).all()
    assert np.isnan(y[4:]).all()
