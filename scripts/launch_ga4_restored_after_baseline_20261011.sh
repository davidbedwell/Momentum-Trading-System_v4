#!/usr/bin/env bash
set -euo pipefail
cd /home/ubuntu/Momentum-Trading-System_v4
BASE=Research/Runs/ga4-normal-oracle-fresh-20261011
OUT=Research/Runs/ga4-normal-restored-20261011
while kill -0 5467 2>/dev/null; do sleep 15; done
.venv/bin/python - "$BASE" <<'PY'
import json,sys,pathlib
p=pathlib.Path(sys.argv[1]);s=json.loads((p/'state.json').read_text())
assert s['generation']==200, f"Baseline incomplete at generation {s['generation']}"
assert not (p/'pending.json').exists(), 'Baseline has unfinished generation'
assert sum(1 for _ in (p/'evaluations.jsonl').open())==1200+200*120, 'Baseline evaluations incomplete'
print('BASELINE_VERIFIED',flush=True)
PY
.venv/bin/python -u scripts/run_ga4_normal_restored_20261011.py --output "$OUT" --generations 1000000 --batch 120 --seed-size 1200 --workers 28 --seed 20261011
