from discovery.competitive_ga.continuous_multiregime_holdout import run,replay

def test_continuous_funded_capital_and_learning_with_frozen_threshold():
    r=run()
    assert r['threshold']==-.03
    assert r['sessions']==192 and r['boundaries']==[64,128,192]
    assert r['prefix_nav_identical'] and r['prefix_decisions_identical']
    assert r['frozen']['return']>r['baseline']['return']
    assert r['frozen']['mdd']<r['baseline']['mdd']
    phases=r['frozen']['phases']
    assert phases[1]['start_nav']==phases[0]['end_nav']
    assert phases[2]['start_nav']==phases[1]['end_nav']
    assert phases[0]['matured_end']<phases[1]['matured_end']<phases[2]['matured_end']
    assert phases[2]['entries']>0
