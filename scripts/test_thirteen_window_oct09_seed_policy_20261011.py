#!/usr/bin/env python3
"""Fail-closed seed policy test; historical domain exceptions must be resolved."""
import json
from scripts.audit_evolution_domains_20261010 import schema,valid
from scripts.thirteen_window_oct09_seeds_20261011 import SOURCE,load
bank=json.loads(SOURCE.read_text());domains=schema()
invalid=[(x['generation'],x['id']) for x in bank['parents'] if not valid(x['chromosomes'],domains)]
assert invalid==[(2,258),(2,946)],invalid
try:load(domains)
except ValueError as e:assert 'OUT_OF_DOMAIN_LEGACY_PARENT' in str(e)
else:raise AssertionError('Noncanonical legacy seed was accepted')
assert len(bank['parents'])==23
print(json.dumps({'status':'PASS_FAIL_CLOSED_SEED_DOMAIN_GUARD','preserved_legacy_count':23,'incompatible':invalid,'integration_status':'BLOCKED_PENDING_DOMAIN_RESOLUTION'}))
