#!/usr/bin/env python3
"""Fail-closed G2 certification entrypoint."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from Core.conforming_ga.preflight import certify

def main():
    result=certify(ROOT,run_tests=True)
    null=ROOT/'Research/Conformance/MTS_H7_NULL_CALIBRATION_20261006.json'
    planted=ROOT/'Research/Conformance/MTS_H7_PLANTED_CALIBRATION_20261006.json'
    for key,path in [('null',null),('planted',planted)]:
        try:
            evidence=json.loads(path.read_text())
            result['checks'][key.upper()+'_EVIDENCE']=evidence.get('passed') is True and evidence.get('status')=='PASS'
        except (OSError,ValueError):
            result['checks'][key.upper()+'_EVIDENCE']=False
    result['passed']=all(result['checks'].values())
    result['status']='PASS' if result['passed'] else 'BLOCKED'
    out=ROOT/'Research/Conformance/MTS_G2_PRODUCTION_CERTIFICATION_20261006.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result['passed'] else 2
if __name__=='__main__':raise SystemExit(main())
