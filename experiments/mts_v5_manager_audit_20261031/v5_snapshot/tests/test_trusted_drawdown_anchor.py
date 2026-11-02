from tests.test_native_replay_bridge import kwargs,proposal
from discovery.competitive_ga.native_replay_bridge import signals_for_close


def evaluate(options):
    return signals_for_close([proposal()],'2020-01-04',**options)[0]


def test_missing_external_trust_anchor_blocks_scaling():
    options=kwargs()
    options.pop('trusted_drawdown_hashes')
    assert evaluate(options).scaling_evidence is None


def test_wrong_external_trust_anchor_blocks_scaling():
    options=kwargs()
    options['trusted_drawdown_hashes']={'cGA7':'incorrect'}
    assert evaluate(options).scaling_evidence is None


def test_matching_external_trust_anchor_allows_evidence():
    assert evaluate(kwargs()).scaling_evidence is not None
