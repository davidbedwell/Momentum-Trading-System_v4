"""Replay evidence gates: no unearned scaling and portfolio risk cap."""
import pytest
from engines.portfolio_replay.kernel import Replay,Bar,Signal
from discovery.competitive_ga.progressive_scaling import ScaleEvidence
from discovery.competitive_ga.manager_order_adapter import orders
from discovery.competitive_ga.manager_policy_v2 import Genes,Proposal

def evidence(n,folds=3,confirmed=True,profitable=True,independent=True,mdd=.1):
    return ScaleEvidence(n,folds,True,mdd,confirmed,profitable,independent)

def seeded():
    r=Replay(cash=90000.,shares={'A':100.})
    return r

def execute_add(requested,ev=None,stop=.02,gap=.03,other=0.):
    r=seeded()
    r.pending=[Signal('A','GA7','c7',requested,scaling_evidence=ev,
        stop_distance=stop if ev else None,gap_risk=gap if ev else None,other_equity_risk=other)]
    r.day('2020-01-02',{'A':Bar(100,100)})
    return r

def test_no_evidence_cannot_scale_past_ten_percent():
    r=execute_add(.30)
    assert r.shares['A']==pytest.approx(100.)
    assert not r.ledger

def test_qualified_evidence_allows_scale_to_thirty_percent():
    r=execute_add(.30,evidence(120))
    assert r.shares['A']==pytest.approx(300.)
    assert r.ledger[0][2]=='BUY'

def test_insufficient_evidence_stays_at_ten_percent():
    r=execute_add(.30,evidence(20))
    assert r.shares['A']==pytest.approx(100.)

def test_risk_budget_restricts_add_even_with_full_evidence():
    r=execute_add(.30,evidence(120),stop=.02,gap=.10,other=.015)
    assert r.shares['A']==pytest.approx(100.)

def test_missing_risk_inputs_fail_closed():
    r=seeded()
    r.pending=[Signal('A','GA7','c7',.20,scaling_evidence=evidence(120))]
    with pytest.raises(ValueError,match='scaling risk inputs required'):
        r.day('2020-01-02',{'A':Bar(100,100)})

def test_manager_adapter_rejects_unverified_above_ten_percent():
    proposal=Proposal('A','c7','GA7','INCREASE',.20,0.,1.,.20,True,120)
    with pytest.raises(ValueError,match='unverified scaling above learning cap'):
        orders([proposal],{'A':.10},.90,Genes())
