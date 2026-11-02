#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
/opt/mts/.venv/bin/python experiments/dev79_rsi_indicator_combinations_20261101/study.py > experiments/dev79_rsi_indicator_combinations_20261101/run.log 2>&1
/opt/mts/.venv/bin/python experiments/dev79_rsi_indicator_combinations_20261101/verify.py > experiments/dev79_rsi_indicator_combinations_20261101/validation.log 2>&1
