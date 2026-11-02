import json
import pytest
from discovery.competitive_ga.nexus_drawdown_adapter import verified_drawdown

class Nexus:
    def __init__(self,record): self.record=record; self.calls=[]
    def get(self,ref,*,verify):
        self.calls.append((ref,verify))
        if ref=='registered-input': return object()
        provenance=type('Provenance',(),{'input_refs':('registered-input',)})()
        envelope=type('Envelope',(),{'schema_id':'mts.equity_marks.v1',
                                     'schema_version':1,'provenance':provenance})()
        return type('Artifact',(),{'payload':json.dumps(self.record).encode(),
                                   'envelope':envelope})()

def record():
    return {'schema':'mts.equity_marks.v1','chromosome_id':'c1',
            'as_of':'2020-01-04','marks':[['2020-01-01',100],['2020-01-03',90]]}

def test_governed_verified_retrieval_and_reconstruction():
    n=Nexus(record())
    evidence,marks,anchor=verified_drawdown(n,'artifact-ref','c1','2020-01-04')
    assert n.calls==[('artifact-ref',True),('registered-input',True)]
    assert evidence.value==pytest.approx(.1)
    assert evidence.source_hash==anchor

@pytest.mark.parametrize('field,value',[
    ('schema','unknown'),('chromosome_id','wrong'),('as_of','2020-01-05'),
    ('marks',[['2020-01-05',90]]),('marks',None)])
def test_invalid_governed_payload_rejected(field,value):
    data=record(); data[field]=value
    with pytest.raises(ValueError): verified_drawdown(Nexus(data),'ref','c1','2020-01-04')

def test_integrity_error_propagates():
    class Broken:
        def get(self,ref,*,verify): raise RuntimeError('integrity failure')
    with pytest.raises(RuntimeError,match='integrity'):
        verified_drawdown(Broken(),'ref','c1','2020-01-04')
