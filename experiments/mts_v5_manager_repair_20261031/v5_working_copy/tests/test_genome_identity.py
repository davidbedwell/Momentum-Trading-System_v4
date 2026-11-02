import pytest
from discovery.competitive_ga.genome_identity import GenomeIdentityRegistry,fingerprint

def test_identity_is_family_scoped_and_genome_bound():
    r=GenomeIdentityRegistry()
    a={'entry':{'threshold':.2},'exit':{'hold':5}}
    same={'exit':{'hold':5},'entry':{'threshold':.2}}
    b={'entry':{'threshold':.3},'exit':{'hold':5}}
    assert fingerprint(a)==fingerprint(same)
    assert r.register('GA6','42',a)==r.require('GA6','42',same)
    with pytest.raises(ValueError,match='reused'):r.register('GA6','42',b)
    with pytest.raises(ValueError,match='mismatch'):r.require('GA6','42',b)
    assert r.register('GA7','42',b)!=r.by_id[('GA6','42')]
    with pytest.raises(ValueError,match='unregistered'):r.require('HORIZONS','42',a)

def test_rejects_incomplete_or_nonnative_identity():
    with pytest.raises(ValueError):fingerprint({})
    with pytest.raises(ValueError):fingerprint({'param':float('nan')})
    with pytest.raises(ValueError):fingerprint({'param':object()})
