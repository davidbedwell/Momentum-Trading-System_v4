#!/usr/bin/env python3
"""Only production entrypoint for the clean conforming GA. Fail closed."""
from pathlib import Path
import sys
REPO=Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0,str(REPO))
import json,sys
from Core.conforming_ga.preflight import require_certified,PreflightFailure
REPO=Path(__file__).resolve().parents[1]
def main():
    try:
        cert=require_certified(REPO)
    except PreflightFailure as exc:
        print("MTS_GA_LAUNCH_BLOCKED")
        print(str(exc))
        return 2
    print("MTS_CERTIFICATION_OK")
    print(json.dumps(cert,sort_keys=True))
    # Evolution is intentionally invoked only by the experiment controller after
    # frozen calibration/fold inputs are registered. This entrypoint cannot bypass certification.
    print("READY_FOR_EXPERIMENT_CONTROLLER")
    return 0
if __name__=="__main__":raise SystemExit(main())
