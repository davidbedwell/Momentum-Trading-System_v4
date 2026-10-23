from pathlib import Path
p=Path('/opt/mts/ga6/policy_evolution_oos.py');s=p.read_text();old="winner=ExitGenes(**history[-1]['genes'])";new="winner=ExitGenes(**max(history,key=lambda h:h['best']['score'])['genes'])";assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
p=Path('/opt/mts/ga6/fitness.py');s=p.read_text();old="if isfinite(improvement) and isfinite(downside):";new="if isfinite(improvement) and isfinite(downside) and improvement>0:";assert s.count(old)==1;s=s.replace(old,new);p.write_text(s)
print('Preserve best trained policy across generations; negative policy does not become mandatory')
