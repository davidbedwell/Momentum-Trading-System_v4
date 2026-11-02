#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
export PYTHONDONTWRITEBYTECODE=1
/opt/mts/.venv/bin/python experiments/rsi_screen_ga6_ga7_feasibility_20261101/replay.py > experiments/rsi_screen_ga6_ga7_feasibility_20261101/run.log 2>&1
/opt/mts/.venv/bin/python experiments/rsi_screen_ga6_ga7_feasibility_20261101/verify.py > experiments/rsi_screen_ga6_ga7_feasibility_20261101/validation.log 2>&1
