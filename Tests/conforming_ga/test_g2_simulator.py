import numpy as np,pandas as pd
from dataclasses import replace
from Core.conforming_ga.g2features import G2Tape
from Core.conforming_ga.g2schema import reduced_linear_g2
from Core.conforming_ga.g2simulator import simulate_g2

def tape(signal=0.02):
    dates=pd.date_range("2026-01-05",periods=6,freq="B")
    T=len(dates);N=1
    stock={"signal":np.full((T,N),signal),"rv20":np.full((T,N),.01),"dist_low20":np.full((T,N),.02)}
    op=np.array([[100.],[101.],[102.],[103.],[104.],[105.]])
    execution={"open":op,"high":op+1,"low":op-1,"close":op,"volume":np.full((T,N),1_000_000.),
               "dividends":np.zeros((T,N)),"safe_daily":np.zeros(T),"adv_dollars":np.full((T,N),100_000_000.)}
    return G2Tape(dates,("X",),stock,{}, {},execution)

def test_g2_simulator_enters_and_respects_gross():
    g=reduced_linear_g2({"signal":1.0})
    r=simulate_g2(g,tape())
    assert len(r.equity)==5
    assert any(any(v>0 for v in w.values()) for w in r.weights)
    assert all(sum(abs(v) for v in w.values())<=1+1e-12 for w in r.weights)
    assert np.all(r.costs>=0)

def test_g2_weak_opportunity_stays_safe():
    g=reduced_linear_g2({"signal":1.0})
    r=simulate_g2(g,tape(signal=-0.02))
    assert all(not w for w in r.weights)
    assert np.allclose(r.safe_weight,1.0)

def test_g2_realistic_cost_is_charged():
    g=reduced_linear_g2({"signal":1.0})
    r=simulate_g2(g,tape())
    assert r.costs[0]>0
