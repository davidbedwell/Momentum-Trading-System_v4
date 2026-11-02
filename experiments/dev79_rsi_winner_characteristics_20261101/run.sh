#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec timeout 900 taskset -c 0 bash -c '
/opt/mts/.venv/bin/python experiments/dev79_rsi_winner_characteristics_20261101/study.py &&
/opt/mts/.venv/bin/python experiments/dev79_rsi_winner_characteristics_20261101/verify.py > experiments/dev79_rsi_winner_characteristics_20261101/validation.log 2>&1
' 
