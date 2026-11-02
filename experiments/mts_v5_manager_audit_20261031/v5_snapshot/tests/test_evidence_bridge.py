from engines.portfolio_replay.kernel import Replay,Bar,Signal
from discovery.competitive_ga.evidence_bridge import MaturedTrade,build_snapshot,to_scale_evidence
import pytest

def records(n=120):
    return [MaturedTrade('chrom','2020-01-01','2020-01-02',.01,'fold'+str(i%4)) for i in range(n)]

def test_only_matured_before_decision_time():
    rows=records(119)+[MaturedTrade('chrom','2020-01-03','2020-01-05',100.,'future')]
    s=build_snapshot('chrom','2020-01-04',rows,historical_mdd=.1,independently_confirmed=True)
    assert s.matured_trades==119 and s.net_ev==pytest.approx(.01)

def test_same_day_maturity_not_available():
    with pytest.raises(ValueError,match='no historical'):
        build_snapshot('chrom','2020-01-02',records(),historical_mdd=.1,independently_confirmed=True)

def test_evidence_drives_actual_scale_up():
    snap=build_snapshot('chrom','2020-01-04',records(),historical_mdd=.1,independently_confirmed=True)
    evidence=to_scale_evidence(snap,signal_confirmed=True,position_profitable=True)
    r=Replay()
    b={'AAA':Bar(100,100)}
    r.day('d1',b,[Signal('AAA','GA7','chrom',.1)])
    r.day('d2',b,[Signal('AAA','GA7','chrom',.3,scaling_evidence=evidence,stop_distance=.04,gap_risk=.05)])
    r.day('d3',b)
    assert .29<r.shares['AAA']*100/(r.cash+r.shares['AAA']*100)<.301

def test_missing_independent_confirmation_blocks_exceptional():
    snap=build_snapshot('chrom','2020-01-04',records(),historical_mdd=.1,independently_confirmed=False)
    evidence=to_scale_evidence(snap,signal_confirmed=True,position_profitable=True)
    from discovery.competitive_ga.progressive_scaling import allowed_target
    assert allowed_target(.1,.3,evidence,stop_distance=.04,gap_risk=.05)==.2
