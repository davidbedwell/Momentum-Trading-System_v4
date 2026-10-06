import numpy as np
from Core.conforming_ga.schema import Genome,Module,StockState,OpportunityMap,Allocation,Lifecycle,ShortPolicy
from Core.conforming_ga.engine import AllocationMode
from Core.conforming_ga.simulator import SessionInput,simulate

def _g():
    term=StockState("signal",1.0)
    return Genome((),(),(term,),(Module("fixture",(term,)),),OpportunityMap(0.0,1.0),
                  Allocation(AllocationMode.STRENGTH,1.0,0.0,1.0,1.0),
                  Lifecycle(1.0,0.0),ShortPolicy(False,0.0))

def _s(day,a,b):
    px={"A":100.0,"B":100.0}
    return SessionInput(when=day,market={},sector={},stock={"A":{"signal":a},"B":{"signal":b}},
        open_t1=px,open_t2=px,high_t={"A":101.0,"B":101.0},low_t={"A":99.0,"B":99.0},
        close_t=px,volume_t={"A":1e6,"B":1e6},dividends_t1_t2={"A":0.0,"B":0.0},
        daily_safe=0.0,daily_borrow={"A":0.0,"B":0.0},
        adv_dollars_t={"A":1e8,"B":1e8},calendar_days=1)

def test_integrated_friction_blocks_marginal_replace():
    sessions=[_s("2026-01-02",2.0,0.0),_s("2026-01-05",1.0,1.006)]
    free=simulate(_g(),sessions,spread_bps=0.0,impact_coefficient=0.0)
    real=simulate(_g(),sessions,spread_bps=None,spread_cap_bps=50.0,impact_coefficient=10.0)
    assert any(m.label=="REPLACE" for m in free.decisions[1])
    assert not any(m.label=="REPLACE" for m in real.decisions[1])
    assert real.weights[1]["A"] > free.weights[1]["A"]

def test_realistic_cost_model_uses_calendar_days_for_safe():
    s=_s("2026-01-02",0.0,0.0)
    s=SessionInput(**{**s.__dict__,"daily_safe":0.01,"calendar_days":3})
    r=simulate(_g(),[s],spread_bps=0.0,impact_coefficient=0.0)
    assert np.isclose(r.equity[-1],100000*(1.01**3))
