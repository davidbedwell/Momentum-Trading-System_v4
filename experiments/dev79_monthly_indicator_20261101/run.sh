#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
exp=experiments/dev79_monthly_indicator_20261101
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
timeout 900 taskset -c 0 /opt/mts/.venv/bin/python -m unittest discover -s "$exp" -p test_experiment.py -v > "$exp/tests.log" 2>&1
timeout 900 taskset -c 0 /opt/mts/.venv/bin/python "$exp/indicator_experiment.py" > "$exp/run.log" 2>&1
timeout 900 taskset -c 0 /opt/mts/.venv/bin/python "$exp/validate_results.py" > "$exp/validation.log" 2>&1
