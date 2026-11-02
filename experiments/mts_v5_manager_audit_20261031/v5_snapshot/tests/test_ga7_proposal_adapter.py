import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,"/opt/mts/ga7-deploy/ga7_audit_v2")
from ga7.proposals import Proposal
from discovery.competitive_ga.ga7_proposal_adapter import from_ga7

def proposal(action="ENTER",weight=.25):
    return Proposal(1,"AAA","ga7_chromosome",action,.7,.05,.02,weight,10,.8)

def test_ga7_request_preserved_for_execution_gate():
    native=from_ga7(proposal(),decision_date="2020-01-03",trained_through="2020-01-02",source_hash="hash",snapshot_hash="snapshot")
    assert native.target_weight==.25
    assert native.native_score_unit=="net_return_fraction"
    assert native.native_score==.05

def test_ga7_pass_and_exit():
    assert from_ga7(proposal("PASS",0),decision_date="2020-01-03",trained_through="2020-01-02",source_hash="hash",snapshot_hash="snapshot") is None
    assert from_ga7(proposal("EXIT",0),decision_date="2020-01-03",trained_through="2020-01-02",source_hash="hash",snapshot_hash="snapshot").target_weight==0
