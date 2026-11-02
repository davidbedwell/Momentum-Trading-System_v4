"""Readiness must remain blocked when evidence is missing, stale or unsealed."""
import json
import pytest
from discovery.competitive_ga.phase4_readiness import matrix,EVIDENCE


def test_missing_evidence_cannot_certify_launch(tmp_path):
    m=matrix(tmp_path)
    assert m['status']=='BLOCKED' and m['authentic_families_ready']==0
    assert len(m['evidence_errors'])==6
    assert all(f['authentic_launch']=='BLOCKED' for f in m['families'].values())


@pytest.mark.parametrize('kind',['stale','proof','different_smoke'])
def test_invalid_evidence_cannot_hide_in_readiness(tmp_path,kind):
    source=tmp_path/'source';source.write_text('fixture')
    for name in EVIDENCE:
        value=dict(status='FIXTURE',deterministic_sha256='fixture')
        if kind=='stale':value['sources']={str(source):'incorrect'}
        if kind=='proof':value['proof_values_read']=True
        if kind=='different_smoke' and name==EVIDENCE[3]:value['deterministic_sha256']='different'
        (tmp_path/name).write_text(json.dumps(value))
    m=matrix(tmp_path)
    assert m['evidence_errors'] and m['status']=='BLOCKED' and m['authentic_families_ready']==0
