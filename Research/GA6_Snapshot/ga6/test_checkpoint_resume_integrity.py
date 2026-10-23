"""Validate actual runner checkpoint structure without altering it."""
import json,base64,pickle,sys
from pathlib import Path
sys.path.insert(0,'/opt/mts');sys.path.insert(0,'/opt/mts/ga5_redesign')
from ga5_chromosome_contract import Genome
p=Path(sys.argv[1]);s=json.loads(p.read_text())
assert s['generation']>=1 and len(s['members'])==s['population']
assert len(s['history'])==s['generation']
assert all(Genome(**m).valid() for m in s['members'])
assert len({Genome(**m).identity() for m in s['members']})==s['population']
rng=pickle.loads(base64.b64decode(s['rng']))
assert isinstance(rng,tuple) and len(rng)==3
print('PASS checkpoint members, identities, generation, history, RNG state')
