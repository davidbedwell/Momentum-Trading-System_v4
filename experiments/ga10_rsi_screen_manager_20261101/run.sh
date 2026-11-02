#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1
/opt/mts/.venv/bin/python -m unittest -v test_ga10.py > tests.log 2>&1
timeout 180 /opt/mts/.venv/bin/python ga10.py > run.log 2>&1
/opt/mts/.venv/bin/python verify.py > verification.log 2>&1
cat run.log
cat verification.log
