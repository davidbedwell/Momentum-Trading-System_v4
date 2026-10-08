[Reading 32 lines from start (total: 32 lines, 0 remaining)]

"""Fail closed before candidate-level risk replay; never load protected price data."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'Research/Runs/layered/stage2-opportunity-v3-20261007'
SPLIT=ROOT/'Research/Partitions/GA4_DEV80_DEV37_FROZEN_SPLIT.json'
CANDIDATES=BASE/'calibration/ga4_frozen_candidate_selection.json'

def audit():
    failures=[]
    manifest=json.loads(SPLIT.read_text()) if SPLIT.is_file() else None
    if manifest is None:
        failures.append('authoritative preselection DEV80/DEV37 membership freeze missing')
    else:
        a=manifest.get('DEV80',[]);b=manifest.get('DEV37',[])
        if len(a)!=80 or len(b)!=37 or len(set(a))!=80 or len(set(b))!=37 or set(a)&set(b):
            failures.append('invalid DEV80/DEV37 split')
        if manifest.get('frozen_before_selection') is not True:
            failures.append('preselection membership provenance unverified')
    selection=json.loads(CANDIDATES.read_text()) if CANDIDATES.is_file() else None
    if selection is None:
        failures.append('frozen candidate genome/selection ledger missing')
    else:
        for key in ('selection_digest','frozen_at','candidate_genomes','attempted_hypotheses','source_sha256'):
            if not selection.get(key):failures.append('candidate selection missing '+key)
    return {'decision':'PASS' if not failures else 'BLOCKED','failures':failures,'protected_price_data_opened':False,
            'candidate_level_replay_verified':False,'independently_verified':False}

if __name__=='__main__':
    result=audit();dest=BASE/'calibration/ga4_candidate_evidence_prerequisite_audit.json'
    dest.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['decision']=='PASS' else 1)
