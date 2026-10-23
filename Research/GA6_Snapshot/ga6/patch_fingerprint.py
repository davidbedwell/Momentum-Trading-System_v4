from pathlib import Path
p=Path('/opt/mts/ga6/runner.py')
s=p.read_text()
needle='+a.entry_mode).encode()).hexdigest()'
assert s.count(needle)==1
names=['niche_evidence.py','path_replay.py','counterfactuals.py','prospective_policy.py','prospective_replay.py','policy_genes.py','policy_research.py','fitness_policy.py','chronological_validation.py']
extra=''.join('+digest_file(Path(__file__).resolve().parent / '+repr(name)+')' for name in names)
p.write_text(s.replace(needle,extra+needle))
print('Updated nine-module fingerprint')
