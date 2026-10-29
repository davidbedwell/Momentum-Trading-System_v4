import ast,importlib.util,json,sys
from pathlib import Path
ROOT=Path("/home/ubuntu/Momentum-Trading-System_v4")
RUN=ROOT/"scripts/run_ga_redesign_approved_20261006.py"
FREEZE=ROOT/"Research/Protocols/MTS_GA_REDESIGN_EXPERIMENT_FREEZE_20261005.md"
def source(): return RUN.read_text()
def test_pf00_traceability_files_exist(): assert RUN.exists() and FREEZE.exists()
def test_pf01_layers_present():
 s=source()
 for x in ("dynamic_peer_context","opportunity","simulate","risk_appetite","safe_margin"): assert x in s
def test_pf03_no_rank_cancellation_architecture():
 s=source(); assert "np.argsort(np.argsort" not in s
def test_pf04_dynamic_peer_pit_and_no_current_gics():
 s=source(); assert "hist=r.iloc[t-window:t+1]" in s; assert "sector:" not in s; tree=ast.parse(s); vals=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]; assert not any("CURRENT_GICS" in v for v in vals)
def test_pf05_exact_allocations():
 s=source(); assert 'ALLOCS=("equal","strength","uncertainty","downside")' in s
def test_pf06_actual_spy_not_partition_alias():
 s=source(); assert "SPY_20050901_20260914_20261006.csv" in s; assert "actual_ew" not in s and "ew_partition" not in s
def test_pf07_comparators_not_predictive_inputs():
 s=source(); assert 'groups={"stock":list(range(ns)),"market":' in s
def test_pf08_cost_sensitivity():
 s=source(); assert "for c in (0,5,10,20)" in s
def test_pf09_short_borrow():
 s=source(); assert "borrow=.003" in s and "shortgross*(borrow/252)" in s
def test_pf10_protected_names_absent():
 s=source()
 for x in ("DV25","A25","A75","B100"):
  # only governance/report text may name them; no loader/path assignment may.
  tree=ast.parse(s); calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]; path_literals=[a.value for n in calls for a in n.args if isinstance(a,ast.Constant) and isinstance(a.value,str)]; assert not any(x in v for v in path_literals)
def test_pf11_four_folds_80_37():
 sys.path.insert(0,str(ROOT/"scripts"));import run_ga_redesign_approved_20261006 as r
 _,_,dev=r.v2.load_dev117();fs=r.folds(dev);assert len(fs)==4 and all(len(a)==80 and len(b)==37 and not(set(a)&set(b)) for a,b in fs)
def test_pf12_all_four_freeze_barrier_before_blind():
 s=source(); assert s.index("assert len(frozen)==4") < s.index("blind=[]")
def test_pf13_time_travel_peer_window():
 s=source(); assert "r.iloc[t-window:t+1]" in s and "r.iloc[t+1" not in s
def test_pf16_17_no_age_hold_cooldown():
 tree=ast.parse(source()); ids={n.id.lower() for n in ast.walk(tree) if isinstance(n,ast.Name)}
 assert not(ids & {"position_age","hold_days","cooldown","entry_date","entry_price"})
def test_pf18_19_no_caps_leverage_options():
 s=source().lower()
 for x in ("position_cap","sector_cap","leverage","options"): assert x not in s
def test_pf20_safe_genuine_and_gross():
 sys.path.insert(0,str(ROOT/"scripts"));import run_ga_redesign_approved_20261006 as r
 import numpy as np
 T,N,F=12,4,6;X=np.full((T,N,F),.5);RX=np.zeros((T,N));rf=np.full(T,.0001)
 g={"modules":[{"family":"x","signal_ids":[0,1],"signal_w":[-4,-4],"gate_ids":[2],"gate_w":[1],"gate_bias":0,"module_w":1}],"opportunity_scale":.01,"risk_appetite_id":3,"risk_appetite_w":0,"risk_appetite_bias":0,"safe_margin":.001,"kappa":1,"uncertainty_penalty":.001,"short":False,"alloc":"equal","gamma":1}
 p,w,to,d=r.simulate(g,X,RX,rf);assert np.all(np.abs(w).sum(1)<=1+1e-12) and np.mean(np.abs(w).sum(1))==0
def test_pf21_lifecycle_semantics():
 s=source()
 for x in ("ENTER","CONTINUE","REPLACE","EXIT_TO_SAFE","SHORT"):assert x in s
def test_pf22_no_ticker_identity_genes():
 s=source();assert '"ticker_id"' not in s and '"cluster_id"' not in s
def test_pf23_sentinel_metric_names():
 s=source();assert "safe_fraction" in s and "turnover" in s
def test_pf24_episodes_present():
 s=source()
 for x in ("GFC","COVID","INFLATION_2022"):assert x in s
def test_pf25_deterministic_seed():
 s=source();assert "hashlib.sha256" in s and "seed(MASTER" in s
def test_primary_fitness_only_cagr_mdd():
 s=source();assert 'def dominates(a,b)' in s and 'a["cagr"]' in s and 'a["mdd"]' in s

def test_pf26_execution_and_realistic_cost():
 s=source();assert "ao.shift(-2)/ao.shift(-1)-1" in s and "Corwin-Schultz" in s and "costmat[t,i]" in s
def test_pf27_nine_islands_and_migration():
 s=source();assert 'kinds=[("band",b) for b in DD]+[("global",None),("novelty",None)]' in s and "ge%25==0" in s and "int(.05*popn)" in s
def test_pf28_multifidelity_validation_frozen():
 p=ROOT/"Research/Reports/MTS_GA_REDESIGN_MULTIFIDELITY_VALIDATION_20261006.json";x=json.loads(p.read_text());assert x["pass"] and all(z["cagr_spearman"]>=.90 and z["mdd_spearman"]>=.90 for z in x["folds"])
