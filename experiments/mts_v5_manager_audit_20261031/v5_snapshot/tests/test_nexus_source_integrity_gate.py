import pytest
from discovery.competitive_ga.nexus_drawdown_adapter import verified_drawdown
from tests.test_nexus_drawdown_adapter import Nexus,record


def test_missing_source_fails_closed():
    nexus=Nexus(record())
    original=nexus.get
    def get(ref,*,verify):
        if ref=='registered-input': raise FileNotFoundError('source unavailable')
        return original(ref,verify=verify)
    nexus.get=get
    with pytest.raises(FileNotFoundError,match='source unavailable'):
        verified_drawdown(nexus,'artifact-ref','c1','2020-01-04')


def test_source_integrity_failure_fails_closed():
    nexus=Nexus(record())
    original=nexus.get
    def get(ref,*,verify):
        if ref=='registered-input':
            assert verify is True
            raise RuntimeError('source checksum mismatch')
        return original(ref,verify=verify)
    nexus.get=get
    with pytest.raises(RuntimeError,match='checksum mismatch'):
        verified_drawdown(nexus,'artifact-ref','c1','2020-01-04')


def test_self_referential_provenance_rejected():
    nexus=Nexus(record())
    original=nexus.get
    def get(ref,*,verify):
        artifact=original(ref,verify=verify)
        if ref=='artifact-ref':
            artifact.envelope.provenance.input_refs=('artifact-ref',)
        return artifact
    nexus.get=get
    with pytest.raises(ValueError,match='self-referential'):
        verified_drawdown(nexus,'artifact-ref','c1','2020-01-04')
