import ast
from pathlib import Path
s=Path('/opt/mts/ga6/runner.py').read_text()
t=ast.parse(s)
assert 'checkpoint_unified.json' in s
assert "Checkpoint fingerprint mismatch" in s
assert 'rng.setstate' in s
assert "tmp.replace(checkpoint)" in s
for name in ('niche_evidence.py','path_replay.py','counterfactuals.py','prospective_policy.py','prospective_replay.py','policy_genes.py','policy_research.py','fitness_policy.py','chronological_validation.py'):
 assert "digest_file(Path(__file__).resolve().parent / '"+name+"')" in s,name
print('PASS checkpoint controls and nine-module cache fingerprint static audit')
