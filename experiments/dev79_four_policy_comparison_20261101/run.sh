#!/bin/bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 ARROW_NUM_THREADS=1
p=experiments/dev79_four_policy_comparison_20261101
/opt/mts/.venv/bin/python "$p/audit_inputs.py" > "$p/input_audit.log" 2>&1
/usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M cpu=%P' -o "$p/runtime.txt" /opt/mts/.venv/bin/python "$p/comparison.py" > "$p/run.log" 2>&1
/opt/mts/.venv/bin/python "$p/verify.py" > "$p/verification.log" 2>&1
/opt/mts/.venv/bin/python -m unittest discover -s "$p" -p test_comparison.py -v > "$p/tests.log" 2>&1
/opt/mts/.venv/bin/python "$p/report.py"
