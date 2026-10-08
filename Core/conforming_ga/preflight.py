"""Single fail-closed certification gate. No override flag exists."""
from __future__ import annotations
from pathlib import Path
import json,subprocess,hashlib
from .availability import *
from .external import *
from .realdata import dev117

class PreflightFailure(RuntimeError):pass

def _passed_report(path:Path)->bool:
    if not path.is_file():return False
    try:
        data=path.read_bytes()
        report=json.loads(data)
        if report.get('passed') is not True:return False
        sidecar=path.with_suffix(path.suffix+'.sha256')
        if not sidecar.is_file():return False
        expected=sidecar.read_text().split()[0]
        if len(expected)!=64 or expected!=hashlib.sha256(data).hexdigest():return False
        return True
    except (OSError,ValueError,TypeError,IndexError):return False

def static_external_checks(repo:Path)->tuple[dict,dict]:
    required={
      "SPY_HASH":sha256(repo/SPY_PATH)==SPY_SHA256,
      "SAFE_HASH":sha256(repo/SAFE_PATH)==SAFE_SHA256,
      "OFR_HASH":ofr_available(repo),
      "DEV117_COUNT":len(dev117(repo))==117,
      "CONTEXTUAL_LAYER_POLICY":contextual_layer_policy_compliant(repo),
      "PIT_EARNINGS_REGISTRY":earnings_registry(repo) is not None,
      "OS_SANDBOX":os_sandbox_available(),
      "NULL_CALIBRATION_REPORT":_passed_report(repo/"Research/Conformance/MTS_H7_NULL_CALIBRATION_20261006.json"),
      "PLANTED_CALIBRATION_REPORT":_passed_report(repo/"Research/Conformance/MTS_H7_PLANTED_CALIBRATION_20261006.json"),
    }
    info={
      "FORMAL_PIT_SECTOR_AVAILABLE":pit_sector_registry(repo) is not None,
      "EARNINGS_REGISTRY_PATH":str(earnings_registry(repo)) if earnings_registry(repo) else None,
      "PIT_SECTOR_REGISTRY_PATH":str(pit_sector_registry(repo)) if pit_sector_registry(repo) else None,
    }
    return required,info

def run_pytest_evidence(repo:Path)->bool:
    p=subprocess.run([str(repo/".venv/bin/python"),"-m","pytest","-q","Tests/conforming_ga"],cwd=repo)
    return p.returncode==0

def certify(repo:Path,*,run_tests=True):
    checks,info=static_external_checks(repo)
    checks["BEHAVIORAL_SUITE"]=run_pytest_evidence(repo) if run_tests else False
    passed=all(checks.values())
    return {"status":"CERTIFIED" if passed else "BLOCKED","checks":checks,"info":info,"passed":passed}

def require_certified(repo:Path):
    r=certify(repo,run_tests=True)
    if not r["passed"]:raise PreflightFailure(json.dumps(r,sort_keys=True))
    return r
