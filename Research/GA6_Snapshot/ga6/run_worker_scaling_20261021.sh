#!/usr/bin/env bash
set -euo pipefail
cd /opt/mts
for workers in 4 8; do
 out="/opt/mts/ga6/runs/ga6_scale_${workers}w_20261021"
 echo "START workers=$workers $(date -u +%FT%TZ)" | tee -a /opt/mts/ga6/runs/worker_scaling_20261021.status
 start=$(date +%s)
 /opt/mts/.venv/bin/python -u ga6/production_runner.py --features /opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet --policy-file /opt/mts/ga5_redesign/exploratory79_policy.json --output "$out" --population 52 --workers "$workers" --generations 1 --stagnation 100 --entry-mode unrestricted --diagnostic-only > "${out}.log" 2>&1
 duration=$(($(date +%s)-start))
 echo "DONE workers=$workers seconds=$duration $(date -u +%FT%TZ)" | tee -a /opt/mts/ga6/runs/worker_scaling_20261021.status
done
