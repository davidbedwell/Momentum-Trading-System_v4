import json,subprocess
from pathlib import Path
p=Path('/opt/mts/ga6/runs/policy_oos_smoke_v6/checkpoint_unified.json')
s=json.loads(p.read_text())
assert s['generation']==1 and len(s['members'])==26
assert len(s['history'])==1
assert len({m['niche'] for m in s['members']})==13
print('PASS persisted generation, population, all niches and history')
