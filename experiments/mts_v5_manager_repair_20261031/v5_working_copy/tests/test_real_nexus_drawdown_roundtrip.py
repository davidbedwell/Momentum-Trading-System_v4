"""Actual SQLite/catalog/filesystem Nexus roundtrip, isolated temporary storage."""
import json
import sys
from pathlib import Path
import pytest
from discovery.competitive_ga.nexus_drawdown_adapter import verified_drawdown

V4=Path('/opt/mts/thunder-migration/Momentum-Trading-System_v4')


def test_real_nexus_publication_and_verified_retrieval(tmp_path,monkeypatch):
    monkeypatch.syspath_prepend(str(V4))
    from Core.research_nexus.bootstrap import ResearchNexusConfig,build_research_nexus
    from Core.research_nexus.models import create_artifact_envelope,Producer,Provenance,ArtifactReference
    nexus=build_research_nexus(ResearchNexusConfig(tmp_path/'nexus'))
    source=create_artifact_envelope(
        artifact_type='EVIDENCE',schema_id='mts.fixture_source.v1',schema_version=1,
        producer=Producer('ENGINE','test-fixture'),provenance=Provenance(),
        lifecycle_state='PUBLISHED',persistence_class='CLASS_I',
        retention_class='PERMANENT',backup_requirement='REQUIRED',
        artifact_id='fixture-input')
    nexus.publish(envelope=source,payload=b'fixture source bytes',media_type='application/octet-stream')
    envelope=create_artifact_envelope(
        artifact_type='EVIDENCE',schema_id='mts.equity_marks.v1',schema_version=1,
        producer=Producer('ENGINE','test-fixture'),
        provenance=Provenance(input_refs=(ArtifactReference('fixture-input',1),)),
        lifecycle_state='PUBLISHED',persistence_class='CLASS_I',
        retention_class='PERMANENT',backup_requirement='REQUIRED')
    record={'schema':'mts.equity_marks.v1','chromosome_id':'c1','as_of':'2020-01-04',
            'marks':[['2020-01-01',100],['2020-01-03',90]]}
    result=nexus.publish(envelope=envelope,payload=json.dumps(record).encode(),media_type='application/json')
    evidence,marks,anchor=verified_drawdown(nexus,result.artifact_ref,'c1','2020-01-04')
    assert evidence.value==pytest.approx(.1)
    assert anchor==evidence.source_hash
    assert len(marks)==2
