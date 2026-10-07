from pathlib import Path

def test_exactly_one_production_null_is_frozen():
    s=Path('Research/G3/MTS_G3_PRODUCTION_DISCOVERY_PROTOCOL_REVISED_20261007.md').read_text()
    amendment=s.split('# User-Approved Prospective Amendment C — 2026-10-07',1)[1]
    assert '1 REAL + 1 matched NULL arm' in amendment
    assert '819,200 maximum total slots' in amendment
    assert 'identical evolutionary search budget' in amendment
    assert 'No other scientific search setting is changed' in amendment

def test_controller_never_authorizes_second_null():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text().lower()
    assert s.count("'--arm','null'") == 1
    assert "'--arm','null2'" not in s and "'--arm','null_2'" not in s
