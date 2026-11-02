#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts/sector-leadership-independent
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
exec timeout 900 /opt/mts/.venv/bin/python experiments/dev79_rsi_fixed_full_2009_2018/study.py
