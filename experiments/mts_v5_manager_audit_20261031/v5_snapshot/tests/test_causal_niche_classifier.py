import pytest
from discovery.competitive_ga.causal_niche_classifier import classify_closes
from discovery.competitive_ga.changing_niche_continuous_trial import run

def test_close_only_niche_changes_with_observed_momentum():
    up=[100+i for i in range(10)]
    down=[100-i for i in range(10)]
    assert classify_closes(up,9,'2026-01-11').controlling('2026-01-11')=='A'
    assert classify_closes(down,9,'2026-01-11').controlling('2026-01-11')=='B'
    with pytest.raises(ValueError):classify_closes(up,8,'2026-01-11')
    with pytest.raises(ValueError):classify_closes(up[:8],9,'2026-01-11')

def test_funded_niche_routing_uses_causal_classifier():
    r=run()
    assert r['niche_changes']>0
    assert r['prefix_nav_identical'] and r['prefix_decisions_identical']
    assert any("'A', 'GA7'" in k for k in r['funded_entries_by_niche_owner'])
    assert any("'B', 'GA6'" in k for k in r['funded_entries_by_niche_owner'])
