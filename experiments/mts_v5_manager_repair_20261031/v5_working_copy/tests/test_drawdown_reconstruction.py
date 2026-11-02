import pytest
from discovery.competitive_ga.drawdown_provenance import reconstruct,verify
from discovery.competitive_ga.native_replay_bridge import signals_for_close
from tests.test_native_replay_bridge import kwargs,proposal

MARKS=[('2020-01-01',100.),('2020-01-02',80.),('2020-01-03',90.)]

def test_drawdown_and_hash_reconstruction():
    dd=reconstruct('cGA7',MARKS,'2020-01-04')
    assert dd.value==pytest.approx(.20)
    assert verify(dd,MARKS,'2020-01-04')
    assert not verify(dd,[('2020-01-01',100.),('2020-01-02',85.),('2020-01-03',90.)],'2020-01-04')

@pytest.mark.parametrize('marks',[
    [('2020-01-04',100.)],
    [('2020-01-02',100.),('2020-01-01',90.)],
    [('2020-01-01',0.)],
    [('2020-01-01',float('nan'))],
])
def test_rejects_noncausal_or_invalid_equity(marks):
    with pytest.raises(ValueError): reconstruct('cGA7',marks,'2020-01-04')

def test_unverified_drawdown_does_not_authorize_scaling():
    opts=kwargs()
    opts['drawdown_marks_by_chromosome']={'cGA7':MARKS}
    result=signals_for_close([proposal()],'2020-01-04',**opts)
    assert result[0].scaling_evidence is None
