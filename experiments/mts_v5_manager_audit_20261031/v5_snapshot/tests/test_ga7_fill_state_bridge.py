import pytest
from engines.portfolio_replay.kernel import Bar
from discovery.competitive_ga.ga7_fill_state_bridge import held_state
from discovery.competitive_ga.ga7_native_daily_producer import produce
from types import SimpleNamespace
G=SimpleNamespace(operator='AND',feature_a='x',feature_b='y',threshold_a=0.,threshold_b=0.,entry_pct=.07,stop_pct=.02,exit_rule='signal_decay',identity=lambda:'ga7-a')

def test_real_fill_to_native_exit():
    bars={'AAA':Bar(100,97)}
    held=held_state({'AAA':70},{'AAA':('GA7','ga7-a')},{'AAA':100.},{'AAA':.02},100000.,bars,'ga7-a')
    native=produce(G,{'AAA':{'close':97,'eligible':True,'features':{'x':.8,'y':.8}}},decision_date='2020-01-03',trained_through='2020-01-02',source_hash='src',snapshot_hash='snap',held=held)
    assert native[0].action=='EXIT'

def test_other_owner_cannot_supply_ga7_position():
    bars={'AAA':Bar(100,97)}
    assert held_state({'AAA':70},{'AAA':('GA6','ga6-a')},{'AAA':100.},{'AAA':.02},100000.,bars,'ga7-a')=={}

def test_missing_fill_basis_fails_closed():
    with pytest.raises(ValueError,match='missing held-position'):
        held_state({'AAA':70},{'AAA':('GA7','ga7-a')},{},{'AAA':.02},100000.,{'AAA':Bar(100,97)},'ga7-a')
