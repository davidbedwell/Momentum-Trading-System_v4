from types import SimpleNamespace
from discovery.competitive_ga.manager_replay_fitness import exit_policy


def test_no_universal_age_exit():
    genes = SimpleNamespace(min_edge=.02, risk_penalty=.2)
    policy = exit_policy(genes)
    held = SimpleNamespace(entry_price=100.)
    for age in (40, 65, 120, 250):
        assert not policy(age, {"close": 125., "volatility": .5}, held)


def test_conditional_risk_exit_remains():
    genes = SimpleNamespace(min_edge=.02, risk_penalty=.2)
    policy = exit_policy(genes)
    held = SimpleNamespace(entry_price=100.)
    assert policy(6, {"close": 95., "volatility": .4}, held)
    assert not policy(4, {"close": 95., "volatility": .4}, held)
