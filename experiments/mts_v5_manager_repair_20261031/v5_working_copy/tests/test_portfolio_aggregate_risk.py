from engines.portfolio_replay.kernel import Replay,Bar,Signal
from discovery.competitive_ga.progressive_scaling import ScaleEvidence

def test_aggregate_risk_budget_across_scale_requests():
    evidence=ScaleEvidence(120,4,True,.10,True,True,True)
    r=Replay(cash=80000,shares={'AAA':100,'BBB':100},max_equity_risk=.02)
    bars={'AAA':Bar(100,100),'BBB':Bar(100,100)}
    signals=[Signal(t,'GA7','c'+t,.30,score=1,scaling_evidence=evidence,
                    stop_distance=.10,gap_risk=.10) for t in ('AAA','BBB')]
    r.day('2020-01-02',bars,signals)
    r.day('2020-01-03',bars)
    # Incremental risk from both requests must not exceed 2% equity.
    incremental=sum(max(0,r.shares[t]*100/100000-.10)*.10 for t in ('AAA','BBB'))
    assert incremental<=.020000001
