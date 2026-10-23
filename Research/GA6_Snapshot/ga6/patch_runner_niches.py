from pathlib import Path
p=Path('/opt/mts/ga6/runner.py');s=p.read_text()
s=s.replace('from ga6.breeder import breed_ga6','from ga6.breeder import breed_ga6\nfrom ga6.niche_evidence import rank_all')
s=s.replace('    scored.sort(key=lambda v:(-v[0],v[1].identity()))','    scored.sort(key=lambda v:(-v[0],v[1].identity()))\n    evidence={g.identity():r.get("ga6_niche_evidence",{}) for _,g,r in scored}\n    if any(set(v)!=set(NICHES) for v in evidence.values()):raise RuntimeError("Incomplete 13-niche evidence")\n    niche_ranks=rank_all(evidence,NICHES)')
s=s.replace('    history[-1][\'niche_counts\']=', '    history[-1]["niche_eligible_counts"]={n:len(niche_ranks[n]) for n in NICHES}\n    history[-1]["niche_leaders"]={n:(niche_ranks[n][0][0] if niche_ranks[n] else None) for n in NICHES}\n    history[-1][\'niche_counts\']=')
p.write_text(s)
print('per-niche rankings wired to GA6 runner')
