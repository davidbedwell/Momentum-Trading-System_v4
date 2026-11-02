from discovery.competitive_ga.frozen_threshold_holdout import run,DISCOVERY,HOLDOUT,THRESHOLDS,objective
from discovery.competitive_ga.multiregime_gate_trial import trial

def test_threshold_selected_only_from_discovery_episodes():
    r=run()
    assert not set(DISCOVERY)&set(HOLDOUT)
    expected=max(THRESHOLDS,key=lambda t:objective([trial(s,t) for s in DISCOVERY]))
    assert r['frozen_threshold']==expected
    assert r['frozen_threshold']==-.03
    assert r['holdout_frozen_objective']>r['holdout_no_gate_objective']
    assert r['holdout']['down_recovery']['frozen']['ga7_entries']>0
