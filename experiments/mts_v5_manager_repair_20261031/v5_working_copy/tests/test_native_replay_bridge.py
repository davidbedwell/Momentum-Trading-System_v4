import pytest
from discovery.competitive_ga.native_signal_contract import NativeProposal
from discovery.competitive_ga.native_replay_bridge import RiskInputs,signals_for_close
from discovery.competitive_ga.evidence_bridge import MaturedTrade,DatedDrawdown
from discovery.competitive_ga.drawdown_provenance import reconstruct
from engines.portfolio_replay.kernel import Replay,Bar

def proposal(family='GA7',ticker='AAA',weight=.30):
    return NativeProposal('2020-01-04',ticker,family,'c'+family,'ADD',weight,.04,
        'net_return_fraction' if family=='GA7' else 'entry_equity_fraction',
        'manifest','snapshot','2020-01-03')

def trades():
    return [MaturedTrade('cGA7','2019-01-01','2019-01-05',.01,'fold'+str(i%4)) for i in range(120)]

def kwargs():
    marks=[('2020-01-01',100.),('2020-01-02',90.),('2020-01-03',95.)]
    return dict(trusted_drawdown_hashes={'cGA7':reconstruct('cGA7',marks,'2020-01-04').source_hash},
        drawdown_marks_by_chromosome={'cGA7':marks},
        trades_by_chromosome={'cGA7':trades()},drawdown_by_chromosome={'cGA7':reconstruct('cGA7',marks,'2020-01-04')},
        independently_confirmed={'cGA7'},held_positions={'AAA':(.10,True)},
        risk_inputs={'AAA':RiskInputs(.04,.05)})

def test_native_chromosome_evidence_to_replay():
    signals=signals_for_close([proposal()],'2020-01-04',**kwargs())
    assert signals[0].scaling_evidence.matured_trades==120
    r=Replay(cash=90000,shares={'AAA':100})
    r.day('2020-01-04',{'AAA':Bar(100,100)},signals)
    r.day('2020-01-05',{'AAA':Bar(100,100)})
    assert .29<r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.301

def test_unverified_history_does_not_earn_thirty():
    x=kwargs();x['trades_by_chromosome']={}
    s=signals_for_close([proposal()],'2020-01-04',**x)
    assert s[0].scaling_evidence is None
    r=Replay(cash=90000,shares={'AAA':100})
    r.day('2020-01-04',{'AAA':Bar(100,100)},s)
    r.day('2020-01-05',{'AAA':Bar(100,100)})
    assert r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.11

def test_cross_family_unscaled_scores_cannot_compete():
    with pytest.raises(ValueError,match='calibrated'):
        signals_for_close([proposal(),proposal('GA6','BBB',.1)],'2020-01-04',**kwargs())

def test_future_or_stale_signal_rejected():
    with pytest.raises(ValueError,match='stale or future'):
        signals_for_close([proposal()],'2020-01-05',**kwargs())
