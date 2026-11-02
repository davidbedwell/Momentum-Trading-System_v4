#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/v5_working_copy"
export PYTHONDONTWRITEBYTECODE=1
/opt/mts/.venv/bin/python -m pytest -q tests/test_manager_repair_end_to_end.py tests/test_portfolio_replay_kernel.py tests/test_progressive_scaling.py tests/test_functional_niche_manager.py tests/test_niche_first_ev_trial.py tests/test_capital_competition.py tests/test_capital_competition_partial.py tests/test_mixed_ga6_ga7_functional.py tests/test_liquidity_policy.py tests/test_paired_defense_functional.py discovery/competitive_ga/test_hierarchical_search.py
