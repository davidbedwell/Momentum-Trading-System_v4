import random, tempfile
from pathlib import Path
import numpy as np
from Core.g3.starter import *

def test_portfolio_metric_firewall():
    try: assert_discovery_payload({"portfolio_CAGR":.3}); assert False
    except ValueError: pass

def test_g2_lineage_firewall():
    for p in ["/tmp/G2/cache.parquet","/x/conforming_ga/features"]:
        try: assert_independent_path(p); assert False
        except ValueError: pass
    assert_independent_path("/data/g3_independent/raw.parquet")

def test_lifecycle_has_scale_down():
    x=np.ones((2,1)); y=np.array([[.03,.03,.03],[.03,.03,.03]])
    g=Specialist(Rule(0,0,1),Rule(0,0,1),1,.2,.2,3,.2,.01)
    o=evaluate_one(g,x,y,0)
    assert any("reduce" in z.actions for z in o)

def test_planted_signal_beats_matched_null():
    x,y,_=planted_dataset(seed=9,n=5000,effect=.01)
    g=Specialist(Rule(0,.7,1),Rule(1,-.3,-1),1,.2,.2,3,.2,.2)
    real=quality(evaluate_one(g,x,y,0))["mean"]
    null=quality(evaluate_one(g,x,temporal_block_permute(y,19,25),0))["mean"]
    assert real>null+.01

def test_checkpoint_restart_identity():
    s={"generation":7,"rng":random.Random(4).getstate(),"archive":[1,2,3]}
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"x.pkl"; h1=checkpoint(p,s); r=restore(p); h2=checkpoint(p,r)
        assert h1==h2 and r["generation"]==7
