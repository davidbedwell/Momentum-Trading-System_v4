from pathlib import Path

def test_controller_formal_gate_is_conforming_only_and_fail_closed():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text()
    assert "PASS_2_OF_3" in s and "STRONG_PASS_3_OF_3" in s
    assert "STOP_V4_FAILED" in s and "RUNNING_V4_PREREGISTERED_GATE" in s
    assert "if cstate not in PASS" not in s
    assert "if g['state'] not in PASS" not in s
    assert "if g['state'] not in PASS" not in s

def test_controller_requires_execution_freeze_and_data():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text()
    assert 'WAIT_PRODUCTION_FREEZE' in s and 'WAIT_DATA_PREP' in s
    assert 'MTS_G3_PRODUCTION_EXECUTION_FREEZE_20261007.sha256' in s

def test_production_runner_has_single_null_and_receiving_reevaluation_path():
    s=Path('scripts/run_g3_production_discovery_20261007.py').read_text()
    assert "choices=['REAL','NULL']" in s
    assert 'gen%20==0' in s and 'mig_candidates' in s
    assert "pops[recv][-1]=mig_candidates[donor]" in s
    assert 'source_rank' not in s and 'source_feasibility' not in s
    assert 'temporal_thirds_positive' in s and 'perturb_positive_fraction' in s

def test_checkpoint_is_hashed_and_benchmark_cannot_pollute_resume():
    s=Path('scripts/run_g3_production_discovery_20261007.py').read_text()
    assert 'CHECKPOINT_HASH_MISMATCH' in s
    assert "if not a.benchmark_only and statep.exists()" in s
    assert "if not a.benchmark_only:" in s and "save_checkpoint(statep" in s
    assert 'SIGALRM' in s and '120' in s

def test_generation10_pareto_pressure_rule_is_executable():
    s=Path('scripts/run_g3_production_discovery_20261007.py').read_text()
    assert 'gen==10 and rank1>.90' in s
    assert 'uncertainty_width' in s and 'rank1_fraction_last_island' in s

def test_preflight_has_cpu_time_and_checkpoint_storage_failstops():
    s=Path('scripts/run_g3_production_controller_20261007.py').read_text()
    assert 'STOP_PARALLEL_UTILIZATION_FAILED' in s
    assert 'STOP_COMPUTE_INFEASIBLE' in s
    assert 'STOP_CHECKPOINT_STORAGE_INFEASIBLE' in s and '500*1024**3' in s

def test_exact_benchmark_uses_descriptor_dev_data():
    s=Path('scripts/run_g3_production_discovery_20261007.py').read_text()
    assert 'if a.benchmark_only:data=dev' in s
    assert 'perturb_positive_fraction' in s
