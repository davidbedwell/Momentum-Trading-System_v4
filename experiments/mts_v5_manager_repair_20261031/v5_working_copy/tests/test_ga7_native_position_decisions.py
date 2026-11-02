from types import SimpleNamespace
import pytest
from discovery.competitive_ga.ga7_native_daily_producer import produce

G=SimpleNamespace(operator='AND',feature_a='x',feature_b='y',threshold_a=0.,threshold_b=0.,entry_pct=.07,stop_pct=.02,exit_rule='signal_decay',identity=lambda:'g7')
def run(x=.8,y=.9,close=100,held=None,defensive=False,genome=G):
    return produce(genome,{'AAA':{'eligible':True,'features':{'x':x,'y':y},'close':close}},decision_date='2020-01-03',trained_through='2020-01-02',source_hash='source',snapshot_hash='snapshot',held=held,defensive=defensive)
def pos(weight=.07):return {'entry':100.,'initial_stop':.02,'weight':weight}

def test_native_hold():
    p=run(x=.6,y=.6,held={'AAA':pos()})[0]
    assert p.action=='HOLD' and p.target_weight==.07

def test_native_stop_and_defense_exit():
    assert run(close=97,held={'AAA':pos()})[0].action=='EXIT'
    assert run(held={'AAA':pos()},defensive=True)[0].action=='EXIT'

def test_native_signal_decay_exit():
    assert run(x=.2,held={'AAA':pos()})[0].action=='EXIT'

def test_native_increase_and_reduce():
    add=run(close=105,held={'AAA':pos()})[0]
    assert add.action=='ADD' and add.target_weight==pytest.approx(.10)
    reduce=run(x=.55,y=.25,held={'AAA':pos()},genome=SimpleNamespace(**{**vars(G),'exit_rule':'reversal'}))[0]
    assert reduce.action=='REDUCE' and reduce.target_weight==pytest.approx(.035)

def test_missing_held_bar_rejected():
    with pytest.raises(ValueError,match='held ticker missing'):
        produce(G,{},decision_date='2020-01-03',trained_through='2020-01-02',source_hash='s',snapshot_hash='h',held={'AAA':pos()})


def test_appreciation_above_order_cap_is_held_without_forced_trim():
    p=run(close=200,held={'AAA':pos(.45)})[0]
    assert p.action=='HOLD'
    assert p.target_weight==.45
