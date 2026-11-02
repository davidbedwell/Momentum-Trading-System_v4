#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
experiment=experiments/dev79_minimal_manager_20261101
python_bin=/opt/mts/.venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 ARROW_NUM_THREADS=1
"$python_bin" "$experiment/audit_inputs.py" > "$experiment/input_audit.log" 2>&1
/usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M cpu=%P' -o "$experiment/runtime.txt" "$python_bin" "$experiment/manager.py" > "$experiment/run.log" 2>&1
"$python_bin" -m unittest discover -s "$experiment" -p 'test_manager.py' -v > "$experiment/tests.log" 2>&1
"$python_bin" "$experiment/summarize.py"
