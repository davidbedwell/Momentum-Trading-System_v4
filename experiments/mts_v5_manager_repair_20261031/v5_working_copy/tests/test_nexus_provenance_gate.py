import pytest
from discovery.competitive_ga.nexus_drawdown_adapter import verified_drawdown
from tests.test_nexus_drawdown_adapter import Nexus,record

@pytest.mark.parametrize('schema,version,inputs',[
    ('wrong',1,('source',)),
    ('mts.equity_marks.v1',2,('source',)),
    ('mts.equity_marks.v1',1,()),
])
def test_missing_or_incorrect_governed_provenance_fails(schema,version,inputs):
    n=Nexus(record())
    original=n.get
    def get(ref,*,verify):
        artifact=original(ref,verify=verify)
        artifact.envelope.schema_id=schema
        artifact.envelope.schema_version=version
        artifact.envelope.provenance.input_refs=inputs
        return artifact
    n.get=get
    with pytest.raises(ValueError,match='governed equity-mark provenance'):
        verified_drawdown(n,'ref','c1','2020-01-04')
