import warnings,numpy as np
from dataclasses import replace
from Core.conforming_ga.g2schema import reduced_linear_g2
from Core.conforming_ga.g2model import evaluate_g2_fields
from Core.conforming_ga.g2fitness import make_g2_evaluator
from Tests.conforming_ga.test_g2_simulator import tape

def test_all_nan_softmax_cell_is_neutral_and_fitness_finite():
    t=tape();t.stock["signal"][0,:]=np.nan
    t.market["spy_dd"]=np.zeros(len(t.dates));t.market["spy_ret1"]=np.zeros(len(t.dates))
    g=reduced_linear_g2({"signal":1.0})
    g=replace(g,aggregator=replace(g.aggregator,mode="softmax"))
    with warnings.catch_warnings():
        warnings.simplefilter("error",RuntimeWarning)
        f=evaluate_g2_fields(g,t)
        m=make_g2_evaluator(t)(g)
    assert f["opportunity_raw"][0,0]==0.0
    assert f["E"][0,0]==0.0
    assert all(np.all(np.isfinite(f[k])) for k in ("E","uncertainty","downside","kappa","q","tau","short_gate"))
    assert all(np.isfinite(v) for v in m.values())
