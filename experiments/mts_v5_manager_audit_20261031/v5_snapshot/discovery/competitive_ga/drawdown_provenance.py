"""Chronological equity-mark drawdown reconstruction for research."""
from datetime import date
from hashlib import sha256
import json
from math import isfinite
from .evidence_bridge import DatedDrawdown

def reconstruct(chromosome_id, marks, as_of):
    cutoff=date.fromisoformat(as_of)
    if not chromosome_id or not marks: raise ValueError('missing marks')
    peak=0.; mdd=0.; previous=None; rows=[]
    for day,equity in marks:
        dt=date.fromisoformat(day); value=float(equity)
        if dt>=cutoff or (previous is not None and dt<=previous):
            raise ValueError('noncausal marks')
        if not isfinite(value) or value<=0: raise ValueError('invalid equity')
        peak=max(peak,value); mdd=max(mdd,1-value/peak)
        rows.append((dt.isoformat(),value)); previous=dt
    payload=json.dumps([chromosome_id,rows],separators=(',',':'))
    return DatedDrawdown(mdd,rows[-1][0],chromosome_id,sha256(payload.encode()).hexdigest())

def verify(evidence,marks,as_of):
    if not isinstance(evidence,DatedDrawdown): return False
    try: return reconstruct(evidence.chromosome_id,marks,as_of)==evidence
    except (ValueError,TypeError,OverflowError): return False
