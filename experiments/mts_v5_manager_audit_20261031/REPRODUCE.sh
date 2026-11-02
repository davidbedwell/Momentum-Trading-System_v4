#!/usr/bin/env bash
set -euo pipefail
AUDIT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_PY=/opt/mts/.venv/bin/python
export PYTHONDONTWRITEBYTECODE=1
export NUMBA_CACHE_DIR=/tmp/mts_v5_audit_numba
cd "$AUDIT_DIR/v5_snapshot"
"$AUDIT_PY" -m pytest -q -p no:cacheprovider tests/test_functional_niche_manager.py tests/test_mixed_ga6_ga7_functional.py tests/test_paired_defense_functional.py tests/test_mixed_capital_competition_trial.py tests/test_capital_competition.py tests/test_capital_competition_partial.py tests/test_capital_risk_policy.py tests/test_liquidity_policy.py tests/test_causal_niche_classifier.py tests/test_competitive_selector_mixed.py tests/test_portfolio_replay_kernel.py tests/test_portfolio_aggregate_risk.py tests/test_native_daily_manager_integration.py tests/test_manager_native_partial_reduction.py tests/test_ga7_missing_stop_rejected.py tests/test_fill_book_residual_shares.py
PYTHONPATH="/opt/mts:$AUDIT_DIR/v5_snapshot" "$AUDIT_PY" -m pytest -q -p no:cacheprovider tests/test_streaming_defense.py tests/test_defense_replay_adapter.py tests/test_native_calibrated_priority_gate.py tests/test_chronological_manager_integrity.py tests/test_causal_ledger.py tests/test_shadow_learning_interface.py
cd "$AUDIT_DIR"
PYTHONPATH="$AUDIT_DIR/reference_snapshot" "$AUDIT_PY" -m pytest -q -p no:cacheprovider reference_snapshot/ga7/test_compiled_portfolio.py reference_snapshot/ga8/test_engine.py -k 'CompiledPortfolioTests or AccountingTests or DividendAndGrammarTests'
PYTHONPATH="$AUDIT_DIR/reference_snapshot" "$AUDIT_PY" -m pytest -q -p no:cacheprovider reference_snapshot/ga7/test_request_replay.py reference_snapshot/ga7/test_integrated_multileg.py
"$AUDIT_PY" audit_smoke.py
"$AUDIT_PY" legacy_smoke.py
