#!/usr/bin/env bash
set -Eeuo pipefail
cd /opt/mts
OUT=/opt/mts/ga6/runs
mkdir -p "$OUT"
LOG="$OUT/launch_$(date -u +%Y%m%dT%H%M%SZ).log"
exec >>"$LOG" 2>&1
trap 'rc=$?; echo "GA6_GATE_FAILED exit=$rc at $(date -u -Is)"; exit "$rc"' ERR
echo "GA6_GATE_STARTED $(date -u -Is)"
sha256sum -c ga6/GA5_BASELINE_SHA256.txt
test -f ga6/test_parity.py
test -f ga6/runner.py
test -f ga6/test_optimizer.py
.venv/bin/python -m pytest -q ga6/test_parity.py ga6/test_optimizer.py
echo "GA6_TESTS_PASS $(date -u -Is)"
.venv/bin/python -u ga6/runner.py --smoke --output "$OUT/smoke"
test -f "$OUT/smoke/SMOKE_PASS.json"
echo "GA6_SMOKE_PASS $(date -u -Is)"
.venv/bin/python -u ga6/runner.py --production --workers 8 --output "$OUT/production"
echo "GA6_RUN_FINISHED $(date -u -Is)"
