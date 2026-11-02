#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON_BIN="${PYTHON_BIN:-/opt/mts/.venv/bin/python}"
OUTPUT="${1:-ga9/artifacts/alpaca_stock_smoke_$(date -u +%Y%m%dT%H%M%S)}"
# Exit 2 is intentional: acquisition never certifies replay inputs.
status=0
"$PYTHON_BIN" -m ga9.alpaca_repair \
  --archive /tmp/ga9_nasdaq_archive \
  --gaps ga9/artifacts/nasdaq_archive_audit_final_20261029/missing_projected_bars.csv \
  --reuse-qqq ga9/artifacts/alpaca_repair_live_batch_20261029 \
  --output "$OUTPUT" --max-requests 2 --max-symbols 1 --max-dates 3 || status=$?
if [[ "$status" != 0 && "$status" != 2 ]]; then exit "$status"; fi
"$PYTHON_BIN" - "$OUTPUT" <<'PY'
import json, sys
from pathlib import Path
r = json.loads((Path(sys.argv[1])/'report.json').read_text())
print(f"RAW recovered: {r['raw_recovered_gaps']}; CERTIFIED recovered: {r['certified_recovered_gaps']}")
assert r['requests'], 'No stock request made; inspect report'
assert len(r['requests']) <= 2
assert all(x['params']['symbols'] != 'QQQ' for x in r['requests'])
assert r['benchmark_rows'] == 1003, 'Unexpected cached QQQ coverage'
assert r['certified_recovered_gaps'] == 0
assert r['raw_recovered_gaps'] > 0, 'No raw stock gaps recovered; inspect sanitized ledger'
print('Tiny live stock repair passed; PIT/replay remains blocked.')
PY
