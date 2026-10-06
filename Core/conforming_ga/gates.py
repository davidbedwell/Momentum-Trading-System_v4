"""Certification barriers and blind ordering for clean MTS."""
from __future__ import annotations
import hashlib, json
from pathlib import Path

class CertificationError(RuntimeError): pass

def sha256_file(path)->str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def freeze_finalists(path, fold:int, payload:dict)->str:
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    body={"fold":fold,"payload":payload}
    raw=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    p.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()

def require_all_fold_freezes(paths:list[str], expected_hashes:list[str]):
    if len(paths)!=4 or len(expected_hashes)!=4: raise CertificationError("exactly four fold freezes required")
    for p,h in zip(paths,expected_hashes):
        if not Path(p).is_file() or sha256_file(p)!=h: raise CertificationError(f"freeze barrier failed: {p}")
    return True

def certification_gate(results:dict[str,bool], required:tuple[str,...]):
    missing=[k for k in required if not results.get(k,False)]
    if missing: raise CertificationError("failed conformance: "+",".join(missing))
    return True
