import json
from pathlib import Path
import scripts.run_g3_automated_stage_controller_20261007 as c

def test_controller_fail_closed_missing(monkeypatch,tmp_path):
    monkeypatch.setattr(c,"A",tmp_path/"missing.json")
    d=None
    try: c.decide()
    except RuntimeError as e: d=str(e)
    assert d and d.startswith("STOP_MISSING:")

def test_power_branch_stationary_bootstrap():
    n=c.required_n_80_one_sided(.018256,.08679972398265211-.082172)
    assert n>80

def test_no_ticker_identity_in_invariants():
    d=c.decide()
    assert "NO_TICKER_IDENTITY_GENE" in d["invariants"]
    assert d["state"] in {"V3_PROTOCOL_FREEZE_REQUIRED","V3_PLANTED_VALIDATION_AUTHORIZED","V3_INFERENTIAL_GATE_AUTHORIZED"}
