from Core.layered_ga.stage2_paired_recovery_v3 import paired_recovery

def synthetic(effect=0.02, shape='FAST'):
    window={'FAST':(3,7),'MEDIUM':(10,20),'SLOW':(25,45)}[shape]
    return {'points':[{'horizon':h,'lcb95':0.01 if window[0]<=h<=window[1] else 0.03,
                       'ev_net':0.025 if h>=62 else 0.012} for h in range(1,64)],
            'paired_delta':[{'horizon':h,'delta_ev_net':effect if window[0]<=h<=window[1] else 0.0}
                            for h in range(1,64)]}

def test_market_background_does_not_hide_fast_signal():
    assert paired_recovery(synthetic(),'FAST',0.02)['pass']

def test_zero_effect_null():
    assert paired_recovery(synthetic(0),'FAST',0)['pass']
    assert not paired_recovery(synthetic(),'FAST',0)['pass']

def test_isolated_peak_fails():
    side=synthetic()
    for p in side['paired_delta']:
        if p['horizon']!=5:p['delta_ev_net']=0
    assert not paired_recovery(side,'FAST',.02)['pass']

def test_missing_positive_lcb_fails():
    side=synthetic()
    for p in side['points']:
        if 3<=p['horizon']<=7:p['lcb95']=-.01
    assert not paired_recovery(side,'FAST',.02)['pass']

def test_incomplete_curve_fails():
    side=synthetic();side['points'].pop()
    assert not paired_recovery(side,'FAST',.02)['pass']
