import numpy as np
from Core.conforming_ga.g2schema import reduced_linear_g2
from Core.conforming_ga.g2simulator import simulate_g2
from Core.conforming_ga.g2fast import fast_simulate_g2
from Tests.conforming_ga.test_g2_simulator import tape

def test_fast_core_matches_reference_equity_cost_turnover():
    g=reduced_linear_g2({"signal":1.0});t=tape()
    slow=simulate_g2(g,t)
    fast=fast_simulate_g2(g,t)
    equity,rets,turn,safe,short,costs,gross,hhi=fast
    assert np.allclose(equity,slow.equity,rtol=1e-11,atol=1e-8)
    assert np.allclose(turn,slow.turnover,rtol=1e-11,atol=1e-12)
    assert np.allclose(safe,slow.safe_weight,rtol=1e-11,atol=1e-12)
    assert np.allclose(costs,slow.costs,rtol=1e-11,atol=1e-8)
