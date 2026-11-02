from discovery.competitive_ga.changing_niche_continuous_trial import run

def test_continuous_manager_routes_multiple_niches_and_chromosomes():
    r=run()
    assert r['sessions']==192
    assert r['niche_changes']>=10
    assert r['native_shadow_outcomes']>100
    assert r['prefix_nav_identical'] and r['prefix_decisions_identical']
    funded=r['funded_entries_by_niche_owner']
    assert any("'A', 'GA6'" in key for key in funded)
    assert any("'A', 'GA7'" in key for key in funded)
    assert any("'B', 'GA6'" in key for key in funded)
    assert any("'B', 'GA7'" in key for key in funded)
