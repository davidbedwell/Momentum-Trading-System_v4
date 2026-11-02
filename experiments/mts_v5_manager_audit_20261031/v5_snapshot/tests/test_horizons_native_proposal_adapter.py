import pytest
from discovery.competitive_ga.horizons_native_proposal_adapter import from_horizons


def convert(transitions,scores=None):
    return from_horizons(transitions,decision_date='2020-02-01',
        chromosome_id='h1',trained_through='2020-01-31',source_hash='manifest',
        snapshot_hash='snapshot',native_score_by_ticker=scores or {'ABC':.7})


def test_native_long_entry_preserves_target_and_provenance():
    rows=convert({'ABC':{'action':'ENTER_LONG','previous_weight':0,'target_weight':.08}})
    assert len(rows)==1
    p=rows[0]
    assert (p.family,p.action,p.target_weight,p.native_score)==('HORIZONS','ENTER',.08,.7)


def test_native_exit_preserved():
    p=convert({'ABC':{'action':'EXIT_LONG','previous_weight':.08,'target_weight':0}})[0]
    assert p.action=='EXIT' and p.target_weight==0


def test_short_and_reversal_fail_closed():
    with pytest.raises(ValueError,match='unsupported'):
        convert({'ABC':{'action':'ENTER_SHORT','previous_weight':0,'target_weight':-.08}})
    with pytest.raises(ValueError,match='unsupported'):
        convert({'ABC':{'action':'REVERSE_TO_LONG','previous_weight':-.08,'target_weight':.08}})


def test_missing_native_score_fails_closed():
    with pytest.raises(ValueError,match='missing native score'):
        convert({'XYZ':{'action':'ENTER_LONG','previous_weight':0,'target_weight':.08}})
