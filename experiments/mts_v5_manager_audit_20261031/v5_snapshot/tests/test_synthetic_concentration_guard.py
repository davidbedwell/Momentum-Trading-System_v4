from discovery.competitive_ga.synthetic_concentration_guard import enforce
from engines.portfolio_replay.kernel import Bar,Signal

def test_overweight_hold_gets_next_open_trim():
    result=enforce([],{'A':12},{'A':Bar(10,10)},1000,{'A':'c'})
    assert len(result)==1 and result[0].target_weight==.10 and result[0].chromosome=='c'

def test_exit_remains_exit_and_normal_position_unchanged():
    exit_signal=Signal('A','GA6','c',0)
    assert enforce([exit_signal],{'A':12},{'A':Bar(10,10)},1000,{'A':'c'})[0].target_weight==0
    assert enforce([],{'A':5},{'A':Bar(10,10)},1000,{'A':'c'})==[]
