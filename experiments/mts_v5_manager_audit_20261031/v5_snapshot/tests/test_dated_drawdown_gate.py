import pytest
from discovery.competitive_ga.evidence_bridge import DatedDrawdown
from tests.test_native_replay_bridge import kwargs,proposal
from discovery.competitive_ga.native_replay_bridge import signals_for_close


def evaluate(dd):
    options=kwargs()
    options['drawdown_by_chromosome']={'cGA7':dd}
    return signals_for_close([proposal()],'2020-01-04',**options)[0]


def test_undated_drawdown_cannot_authorize_scaling():
    assert evaluate(.10).scaling_evidence is None


@pytest.mark.parametrize('dd',[
    DatedDrawdown(.1,'2020-01-04','cGA7','hash'),
    DatedDrawdown(.1,'2020-01-05','cGA7','hash'),
    DatedDrawdown(.1,'2020-01-03','wrong','hash'),
    DatedDrawdown(.1,'2020-01-03','cGA7',''),
    DatedDrawdown(float('nan'),'2020-01-03','cGA7','hash'),
])
def test_invalid_drawdown_provenance_rejected(dd):
    with pytest.raises(ValueError,match='drawdown provenance'):
        evaluate(dd)


def test_prior_dated_drawdown_can_supply_scaling_evidence():
    assert evaluate(kwargs()['drawdown_by_chromosome']['cGA7']).scaling_evidence is not None
