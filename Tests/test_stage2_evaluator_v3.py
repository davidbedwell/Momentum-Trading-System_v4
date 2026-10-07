import numpy as np
from Core.layered_ga.stage2_path_v3 import ExecutionPaths,ProspectiveCosts
from Core.layered_ga.stage2_evaluator_v3 import evaluate_curve,_pareto_indices

def test_curve_uses_all_integer_horizons_and_pareto_keeps_tradeoffs():
    n=400;H=4
    # Horizon EV rises, but adverse excursion worsens; none should dominate all others.
    endpoint=np.tile(np.array([.01,.02,.03,.04],np.float32),(n,1))
    low=np.tile(np.array([-.002,-.005,-.01,-.02],np.float32),(n,1));high=np.tile(np.array([.02,.03,.04,.05],np.float32),(n,1))
    days=np.tile(np.array([1,2,3,4],np.int16),(n,1));p=ExecutionPaths(endpoint,low,high,days)
    z=np.zeros((n,H),np.float32);c=ProspectiveCosts(z,z,np.zeros(n),np.zeros(n),np.ones(n),np.zeros(n))
    clusters=np.arange(n,dtype=np.int32);ev=evaluate_curve(np.ones(n,bool),p,c,'LONG',clusters)
    assert len(ev.points)==4
    assert ev.pareto_horizons==(1,2,3,4)

def test_dominated_horizon_removed():
    pts=[{'ev_net':.01,'lcb95':.008,'mae_mean':-.01},{'ev_net':.009,'lcb95':.007,'mae_mean':-.02}]
    assert _pareto_indices(pts)==[0]

def test_short_orientation_and_costs_are_independent():
    n=400;ep=np.full((n,1),-.02,np.float32);lo=np.full((n,1),-.03,np.float32);hi=np.full((n,1),.01,np.float32);days=np.ones((n,1),np.int16)
    p=ExecutionPaths(ep,lo,hi,days);lc=np.full((n,1),.001,np.float32);sc=np.full((n,1),.002,np.float32);c=ProspectiveCosts(lc,sc,np.zeros(n),np.zeros(n),np.ones(n),np.zeros(n))
    e=evaluate_curve(np.ones(n,bool),p,c,'SHORT',np.arange(n,dtype=np.int32))
    assert np.isclose(e.points[0]['ev_net'],.018,atol=1e-6)
    assert np.isclose(e.points[0]['mae_mean'],-.01,atol=1e-6)
    assert np.isclose(e.points[0]['mfe_mean'],.03,atol=1e-6)
