from discovery.competitive_ga.reversal_response_diagnostic import run

def test_reversal_exposes_unresponsive_entry_policy():
    r=run()
    assert r['momentum_detection_lag']==3
    assert r['first_funded_learning_divergence']<r['boundary_session']
    assert r['learned']['entries_after']['GA7']>0
    assert r['learned']['entries_after']['NO_ENTRY']==0
    assert r['learned']['post_boundary_return']<r['baseline']['post_boundary_return']
    assert r['learned']['max_drawdown']>r['baseline']['max_drawdown']
