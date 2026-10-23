from pathlib import Path
p=Path('/opt/mts/ga6/breeder.py');s=p.read_text()
s=s.replace('def breed_ga6(scored,rng,population):','def breed_ga6(scored,rng,population,niche_ranks=None):')
s=s.replace(' by={n:[x[1] for x in ranked if x[1].niche==n] for n in NICHES}',' by={n:[x[1] for x in ranked if x[1].niche==n] for n in NICHES}\n if niche_ranks is not None:\n  genome_by_id={g.identity():g for _,g,_ in scored}\n  for n in NICHES:\n   specialists=[replace(genome_by_id[gid],niche=n) for gid,_ in niche_ranks[n][:max(1,population//len(NICHES))] if gid in genome_by_id]\n   by[n]=specialists+by[n]')
s=s.replace("'selection':'ga6_ev'","'selection':'ga6_niche_ev' if niche_ranks is not None else 'ga6_ev'")
p.write_text(s)
r=Path('/opt/mts/ga6/runner.py');v=r.read_text().replace('breed_ga6(scored,rng,a.population)','breed_ga6(scored,rng,a.population,niche_ranks)');r.write_text(v)
print('niche specialists connected to breeding')
