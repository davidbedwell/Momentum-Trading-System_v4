#!/usr/bin/env bash
set -euo pipefail
cd /home/ubuntu/mts-layered-run-20261007
PHASE=Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009
while [ ! -f "$PHASE/manifest.json" ]; do
  if ! pgrep -f '^python3 scripts/run_gen1_phase_b_dev80_20261009.py$' >/dev/null; then echo 'PHASE_B_STOPPED_WITHOUT_MANIFEST'; exit 1; fi
  sleep 10
done
python3 - <<'PY'
import json
p='Research/Runs/gen1-merit-screen-20261008/phaseB_dev80_126_20261009/manifest.json'
m=json.load(open(p))
assert m['status']=='OUTCOME_EXTENSION_BUILT_NOT_CERTIFIED' and all(m['prefix_comparisons'].values())
PY
PYTHONPATH=. python3 scripts/run_gen1_phase_b_parent_study_20261009.py
