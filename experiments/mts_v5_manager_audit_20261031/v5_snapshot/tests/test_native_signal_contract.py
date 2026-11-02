import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"discovery"/"competitive_ga"))
from native_signal_contract import NativeProposal,normalize_proposals

def p(family="GA6",unit="entry_equity_fraction",trained="2020-01-01",action="ENTER",weight=.1):
    return NativeProposal("2020-01-03","AAA",family,"chromosome",action,weight,.05,unit,"sourcehash","featurehash",trained)

def test_preserves_native_score_and_identity():
    assert normalize_proposals([p()],"2020-01-03")[0].native_score==.05

def test_rejects_mixed_native_score_units():
    with pytest.raises(ValueError,match="unit"):p("GA7","entry_equity_fraction")
    assert p("GA7","r_multiple").native_score_unit=="r_multiple"

def test_rejects_future_trained_model():
    with pytest.raises(ValueError,match="future"):p(trained="2020-01-04")

def test_rejects_future_or_stale_decision():
    with pytest.raises(ValueError,match="stale"):normalize_proposals([p()],"2020-01-02")

def test_exit_and_cap_validation():
    with pytest.raises(ValueError,match="zero"):p(action="EXIT")
    with pytest.raises(ValueError,match="values"):p(weight=.31)
