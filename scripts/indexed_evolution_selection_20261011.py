"""Selection index: one validity scan, one eligibility pass per horizon, exact overlap semantics."""
from scripts.audit_evolution_domains_20261010 import valid
from scripts.run_evolution_v2_20261010 import qualify

def indexed_niches(genomes,results,domains,horizons,side='LONG'):
    hs=tuple(horizons)
    eligible=[]
    for k,c in genomes.items():
        r=results.get(k)
        if c['side']==side and r and r.get('signal') and r['signal']['count']>=30 and valid(c['chromosomes'],domains):
            s=r['signal']; eligible.append((k,c,r,int.from_bytes(bytes.fromhex(s['bits']),'big'),s['size']))
    niches=[]
    for h in hs:
        options=[]
        for k,c,r,b,n in eligible:
            q=qualify(r,h)
            if q:options.append((q,k,c,r,b,n))
        options.sort(key=lambda t:(-t[0][0],-t[0][1],t[1]))
        winners=[];active=set()
        for q,k,c,r,b,n in options:
            duplicate=False
            for wb,wn in winners:
                if n!=wn:raise ValueError('Different observation universes')
                union=(b|wb).bit_count()
                ratio=(b&wb).bit_count()/union if union else 1.0
                if ratio>=.85:duplicate=True;break
            if not duplicate:winners.append((b,n));active.add(k)
        # pool_for original ordering: stable sort on q, then greedy strict < .85
        ranked=sorted(((qualify(r,h),k,c,r,b,n) for k,c,r,b,n in eligible if qualify(r,h)),key=lambda t:t[0],reverse=True)
        chosen=[]; chosen_bits=[]
        for q,k,c,r,b,n in ranked:
            if all(((b&old_b).bit_count()/((b|old_b).bit_count()) if (b|old_b) else 1.0)<.85 for old_b in chosen_bits):
                chosen.append((q,c,r));chosen_bits.append(b)
            if len(chosen)>=20:break
        chosen=[x for x in chosen if x[1]['genome_hash'] in active]
        if len(chosen)>=2:niches.append((h,chosen))
    return niches
