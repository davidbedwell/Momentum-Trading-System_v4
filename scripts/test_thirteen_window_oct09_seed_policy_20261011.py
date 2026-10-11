#!/usr/bin/env python3
"""Frozen 1200 random + 23 legacy, hash and lineage, restart determinism."""
import json,random
from scripts.audit_evolution_domains_20261010 import schema,valid
from scripts.thirteen_window_oct09_seeds_20261011 import SOURCE,load,seed_population
from scripts.run_thirteen_window_normal_20261011 import fresh
bank=json.loads(SOURCE.read_text());domains=schema()
assert len(bank['parents'])==23
legacy,sha=load(domains)
assert len(legacy)==23 and len({x['genome_hash'] for x in legacy})==23
assert {(x['legacy_generation'],x['legacy_id']) for x in legacy}.issuperset({(1,1660),(2,766),(2,644),(2,818)})
assert not {(2,258),(2,946)}.intersection({(x['legacy_generation'],x['legacy_id']) for x in legacy})
assert all(valid(x['chromosomes'],domains) for x in legacy)
# Small deterministic integration check; production size is configured at 1200.
a,sa=seed_population(random.Random(20261011),domains,30,fresh)
b,sb=seed_population(random.Random(20261011),domains,30,fresh)
assert sa==sb==sha and a==b and len(a)==53
assert len({x['genome_hash'] for x in a})==53
assert sum(x['seed_origin']=='FRESH_RANDOM' for x in a)==30
assert sum(x['seed_origin']=='OCT09_LEGACY' for x in a)==23
assert all(x['generation']==0 for x in a)
print(json.dumps({'status':'PASS_SEED_INTEGRATION','legacy':23,'random_tested':30,'production_random_config':1200,'production_expected':1223,'source_sha256':sha,'full_1200_generated':False}))
