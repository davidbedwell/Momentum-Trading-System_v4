#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 ARROW_NUM_THREADS=1
CPU=$(/opt/mts/.venv/bin/python -c 'import os; print(min(os.sched_getaffinity(0)))')
exec taskset -c "$CPU" timeout 1150 /usr/bin/time -v bash -c '/opt/mts/.venv/bin/python comparison.py > replay.log && /opt/mts/.venv/bin/python study.py > analysis.log && /opt/mts/.venv/bin/python strata.py && /opt/mts/.venv/bin/python -m unittest test_comparison test_study -v > tests.log 2>&1 && /opt/mts/.venv/bin/python finalize.py'
