import ast
from pathlib import Path

def test_controller_has_machine_pass_and_fail_closed():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text()
    assert "PASS_2_OF_3" in s and "STRONG_PASS_3_OF_3" in s and "STOP_V3_FAILED" in s
    assert "WAIT_PRODUCTION_FREEZE" in s and "WAIT_DATA_PREP" in s and "RUNNING_EXACT_BENCHMARK" in s
    ast.parse(s)

def test_controller_launches_production_not_transport():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text()
    assert 'run_g3_production_discovery_20261007.py' in s
    assert 'transport' not in s.lower()
