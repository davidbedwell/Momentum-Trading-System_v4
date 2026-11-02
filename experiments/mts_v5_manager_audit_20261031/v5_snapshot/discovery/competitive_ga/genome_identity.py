"""Strict identity for native chromosome genomes; IDs are not genome hashes.
Callers must supply complete native genome definitions, not candidate metadata.
"""
import hashlib
import json
from math import isfinite

def _check(value):
    if value is None or isinstance(value,(str,bool,int)):
        return
    if isinstance(value,float):
        if not isfinite(value):raise ValueError('nonfinite genome parameter')
        return
    if isinstance(value,list):
        for item in value:_check(item)
        return
    if isinstance(value,dict):
        if any(not isinstance(k,str) for k in value):raise ValueError('genome keys must be strings')
        for item in value.values():_check(item)
        return
    raise ValueError('genome must be JSON-native, not a representation string')

def fingerprint(genome):
    if not isinstance(genome,dict) or not genome:raise ValueError('complete genome mapping required')
    _check(genome)
    canonical=json.dumps(genome,sort_keys=True,separators=(',',':'),allow_nan=False)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()

class GenomeIdentityRegistry:
    def __init__(self):self.by_id={}
    def register(self,family,chromosome_id,genome):
        if not family or not chromosome_id:raise ValueError('family and ID required')
        digest=fingerprint(genome)
        key=(family,chromosome_id)
        if key in self.by_id and self.by_id[key]!=digest:
            raise ValueError('chromosome ID reused for different genome')
        self.by_id[key]=digest
        return digest
    def require(self,family,chromosome_id,genome):
        key=(family,chromosome_id)
        if key not in self.by_id:raise ValueError('unregistered chromosome genome')
        if fingerprint(genome)!=self.by_id[key]:raise ValueError('chromosome genome mismatch')
        return self.by_id[key]
