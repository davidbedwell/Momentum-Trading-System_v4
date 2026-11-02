import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"discovery"/"competitive_ga"))
from progressive_scaling import ScaleEvidence,allowed_target

def evidence(**changes):
    base=dict(matured_trades=120,forward_folds=4,positive_net_ev=True,historical_mdd=.10,current_signal_confirmed=True,position_profitable=True,independent_confirmation=True)
    base.update(changes)
    return ScaleEvidence(**base)

def test_initial_entry_cannot_exceed_ten_percent():
    assert allowed_target(0,.30,evidence(),stop_distance=.04,gap_risk=.04)==.10

def test_exceptional_winner_can_scale_to_thirty():
    assert allowed_target(.10,.30,evidence(),stop_distance=.04,gap_risk=.05)==.30

def test_weak_history_does_not_qualify():
    assert allowed_target(.10,.30,evidence(matured_trades=10),stop_distance=.04,gap_risk=.05)==.10

def test_no_scaling_losing_position():
    assert allowed_target(.10,.30,evidence(position_profitable=False),stop_distance=.04,gap_risk=.05)==.10

def test_gap_risk_limits_position():
    assert allowed_target(.10,.30,evidence(),stop_distance=.02,gap_risk=.10)==pytest.approx(.20)

def test_other_portfolio_risk_reduces_allowance():
    assert allowed_target(.10,.30,evidence(),stop_distance=.04,gap_risk=.05,other_equity_risk=.01)==pytest.approx(.20)

def test_unconfirmed_cannot_scale():
    assert allowed_target(.10,.30,evidence(current_signal_confirmed=False),stop_distance=.04,gap_risk=.05)==.10
