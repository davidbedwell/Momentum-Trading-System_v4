"""Idempotent GA5 DEV79 niche migration; preserves legacy snapshots."""
from pathlib import Path
r=Path('/opt/mts');contract=r/'ga5_chromosome_contract.py';s=contract.read_text();old='self.niche in {"growth","trend","rotation","range","decline","crash","recovery"}';new='self.niche in {f"NICHE-{i:04d}" for i in range(1,14)}';assert old in s or new in s;s=s.replace(old,new);contract.write_text(s)
opt=r/'ga5_redesign/optimizer_v3.py';s=opt.read_text();old='NICHES=("growth","trend","rotation","range","decline","crash","recovery")';new='NICHES=tuple(f"NICHE-{i:04d}" for i in range(1,14))';assert old in s or new in s;opt.write_text(s.replace(old,new))
seeds=r/'ga5_redesign/niche_seeds.py';s=seeds.read_text();s=s.replace('g=replace(seed(niche),**CONFIG[niche],','g=replace(seed(niche),**CONFIG[list(CONFIG)[(int(niche[-4:])-1)%len(CONFIG)]],');seeds.write_text(s)
print('MIGRATED 13 niche IDs; legacy seed feature templates retained as initialization only')
