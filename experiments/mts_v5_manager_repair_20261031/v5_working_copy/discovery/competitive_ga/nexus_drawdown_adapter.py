"""Fail-closed bridge from verified Research Nexus equity marks to replay evidence.

Caller supplies a governed artifact reference, not a filesystem location.
"""
import json
from .drawdown_provenance import reconstruct


def verified_drawdown(nexus, artifact_ref, chromosome_id, as_of):
    artifact=nexus.get(artifact_ref, verify=True)
    envelope=artifact.envelope
    if (envelope.schema_id!='mts.equity_marks.v1' or envelope.schema_version!=1
        or not envelope.provenance.input_refs):
        raise ValueError('missing governed equity-mark provenance')
    for source_ref in envelope.provenance.input_refs:
        if source_ref == artifact_ref:
            raise ValueError('self-referential source')
        nexus.get(source_ref, verify=True)
    record=json.loads(artifact.payload)
    if not isinstance(record,dict) or record.get('schema')!='mts.equity_marks.v1':
        raise ValueError('wrong equity-mark schema')
    if record.get('chromosome_id')!=chromosome_id:
        raise ValueError('equity-mark chromosome mismatch')
    if record.get('as_of')!=as_of:
        raise ValueError('equity-mark decision date mismatch')
    if not isinstance(record.get('marks'),list):
        raise ValueError('missing equity marks')
    marks=record['marks']
    evidence=reconstruct(chromosome_id,marks,as_of)
    return evidence,marks,evidence.source_hash
