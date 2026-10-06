#!/usr/bin/env python3
from pathlib import Path
import sys
REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
import json
from Core.conforming_ga.preflight import certify
REPO=Path(__file__).resolve().parents[1]
r=certify(REPO,run_tests=True)
print(json.dumps(r,indent=2,sort_keys=True))
raise SystemExit(0 if r["passed"] else 2)
