#!/usr/bin/env python3
"""Production launch gate: never claim GA execution from certification alone."""
from pathlib import Path
import json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
CERT=ROOT/'Research/Conformance/MTS_G2_PRODUCTION_CERTIFICATION_20261006.json'
def main():
    try:
        report=json.loads(CERT.read_text())
    except (OSError,ValueError):
        print('PRODUCTION_BLOCKED: certification missing or unreadable',file=sys.stderr)
        return 2
    sidecar=CERT.with_suffix(CERT.suffix+'.sha256')
    try:
        digest=sidecar.read_text().split()[0]
        if len(digest)!=64 or digest!=hashlib.sha256(CERT.read_bytes()).hexdigest():
            print('PRODUCTION_BLOCKED: certification integrity mismatch',file=sys.stderr)
            return 2
    except (OSError,IndexError):
        print('PRODUCTION_BLOCKED: certification integrity missing',file=sys.stderr)
        return 2
    if report.get('passed') is not True or report.get('status')!='PASS':
        print('PRODUCTION_BLOCKED: certification not passed',file=sys.stderr)
        return 2
    print('PRODUCTION_BLOCKED: certified production execution controller not implemented',file=sys.stderr)
    return 2
if __name__=='__main__':raise SystemExit(main())
