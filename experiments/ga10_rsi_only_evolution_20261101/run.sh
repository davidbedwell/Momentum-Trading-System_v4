#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
/opt/mts/.venv/bin/python -m unittest -v test_study.py > tests.log 2>&1
/opt/mts/.venv/bin/python -u study.py >> run.log 2>&1

/opt/mts/.venv/bin/python verify.py > verification.log 2>&1
/opt/mts/.venv/bin/python finalize.py > finalization.log 2>&1
