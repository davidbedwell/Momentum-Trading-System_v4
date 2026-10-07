import numpy as np, pandas as pd
from Core.layered_ga.stage2_path_v3 import build_execution_paths,build_prospective_costs,signed_excursions

def fixture():
    dates=pd.bdate_range('2026-01-02',periods=30)
    # deterministic +1% each business-day open; intraday +/-1% around open, no adjustment difference
    op=100*(1.01**np.arange(30)); close=op.copy()
    return pd.DataFrame({'security_id':['X']*30,'date':dates,'open':op,'high':op*1.01,'low':op*.99,'close':close,'adj_close':close,'volume':[1_000_000]*30})

def test_tplus1_open_horizons_and_excursions():
    d=fixture();p=build_execution_paths(d,max_horizon=3)
    assert np.isclose(p.endpoint_return[0,0],.01,rtol=1e-5)
    assert np.isclose(p.endpoint_return[0,2],1.01**3-1,rtol=1e-5)
    # Entry at row1 open. First held session low/high are +/-1% from that entry.
    assert np.isclose(p.low_excursion[0,0],-.01,atol=1e-6)
    assert np.isclose(p.high_excursion[0,0],.01,atol=1e-6)
    smae,smfe=signed_excursions(p,'SHORT')
    assert np.isclose(smae[0,0],-.01,atol=1e-6)
    assert np.isclose(smfe[0,0],.01,atol=1e-6)

def test_costs_are_causal_and_short_borrow_grows_with_calendar_days():
    d=fixture();p=build_execution_paths(d,max_horizon=3);c=build_prospective_costs(d,p)
    assert np.isfinite(c.long_roundtrip[20,0])
    assert c.long_roundtrip[20,0] == c.long_roundtrip[20,2]
    assert c.short_roundtrip[20,2] > c.short_roundtrip[20,0]
    # spread proxy: high-low=2% of open ~=close => half range ~100bps, capped at 50.
    assert np.isclose(c.spread_bps[20],50.0)

def test_no_cross_security_path_bleed():
    a=fixture().iloc[:8].copy();b=fixture().iloc[:8].copy();b['security_id']='Y';b['open']*=10;b['close']*=10;b['adj_close']*=10;b['high']*=10;b['low']*=10
    d=pd.concat([a,b],ignore_index=True).sort_values(['date','security_id']).reset_index(drop=True)
    p=build_execution_paths(d,max_horizon=3)
    # Both securities have identical percentage paths despite interleaving rows.
    for sec in ['X','Y']:
        ix=d.index[d.security_id.eq(sec)][0]
        assert np.isclose(p.endpoint_return[ix,2],1.01**3-1,rtol=1e-5)


def test_pre_registered_sec_rate_is_unknown_not_fabricated():
    d=fixture().copy();d['date']=pd.bdate_range('2004-10-01',periods=len(d))
    p=build_execution_paths(d,max_horizon=3);c=build_prospective_costs(d,p)
    assert np.isnan(c.regulatory_sell_fraction[20])
    assert np.isnan(c.long_roundtrip[20,0])
    assert np.isnan(c.short_roundtrip[20,0])
