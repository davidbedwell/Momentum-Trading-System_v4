from pathlib import Path
p=Path('/opt/mts/ga6/runner.py');s=p.read_text()
needle='+a.entry_mode).encode()).hexdigest()'
assert s.count(needle)==1
for name in ('policy_evolution_oos.py',):
 token="+digest_file(Path(__file__).resolve().parent / '"+name+"')"
 if token not in s:s=s.replace(needle,token+needle)
p.write_text(s)
print('Added OOS policy evolution to engine fingerprint')
