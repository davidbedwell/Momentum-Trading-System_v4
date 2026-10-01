from pathlib import Path


def test_one_ticker_preflight_script_exists_and_is_fail_closed():
    text=Path("scripts/preflight_one_ticker_computational_search.py").read_text()
    assert "ADAPTIVE_SEARCH_PROHIBITED" in text
    assert "PREDICTOR_V2_MISSING" in text
    assert "OUTCOME_V1_MISSING" in text
    assert "PREFLIGHT_PASS=True" in text


def test_one_ticker_runner_has_zero_sol_calls_and_discovery_gate():
    text=Path("scripts/run_one_ticker_computational_search.py").read_text()
    assert 'scientific_cohort="DISCOVERY"' in text
    assert "SOL_CALLS=0" in text
    assert "EVENT_EARNINGS_ALPHA_SEARCH" in text
    assert "BLOCKED_UNTIL_PIT_SCHEDULED_EARNINGS_CALENDAR" in text
