import hashlib,json
from Core.conforming_ga.preflight import _passed_report

def test_missing_sidecar_is_rejected(tmp_path):
    p=tmp_path/'evidence.json'
    p.write_text(json.dumps({'passed':True}))
    assert not _passed_report(p)

def test_tampered_report_is_rejected(tmp_path):
    p=tmp_path/'evidence.json'
    p.write_text(json.dumps({'passed':True}))
    p.with_suffix('.json.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'\n')
    assert _passed_report(p)
    p.write_text(json.dumps({'passed':True,'tampered':True}))
    assert not _passed_report(p)

def test_failed_evidence_is_rejected_even_with_matching_hash(tmp_path):
    p=tmp_path/'evidence.json'
    p.write_text(json.dumps({'passed':False}))
    p.with_suffix('.json.sha256').write_text(hashlib.sha256(p.read_bytes()).hexdigest()+'\n')
    assert not _passed_report(p)
