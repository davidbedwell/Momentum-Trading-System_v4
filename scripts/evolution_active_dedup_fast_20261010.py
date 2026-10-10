"""Exact Jaccard-equivalent accelerated population curation; no scientific gate changes."""
from scripts.run_evolution_v2_20261010 import qualify

def curate(genomes,results,domains,horizons,threshold=.85):
 from scripts.audit_evolution_domains_20261010 import valid
 active=[];removed=[];bits={}
 def packed(k,r):
  if k not in bits:
   s=r['signal'];bits[k]=(int.from_bytes(bytes.fromhex(s['bits']),'big'),s['size'])
  return bits[k]
 for side in ('LONG','SHORT'):
  for h in horizons:
   options=[]
   for k,c in genomes.items():
    r=results.get(k)
    if c['side']!=side or not valid(c['chromosomes'],domains) or not r or not r.get('signal'):continue
    q=qualify(r,h)
    if q and r['signal']['count']>=30:options.append((q,k,c,r))
   options.sort(key=lambda t:(-t[0][0],-t[0][1],t[1]))
   winners=[]
   for q,k,c,r in options:
    x,n=packed(k,r);duplicate=None
    for w in winners:
     y,m=packed(w[1],w[3])
     if n!=m:raise ValueError('Different observation universes')
     union=(x|y).bit_count()
     ratio=(x&y).bit_count()/union if union else 1.0
     if ratio>=threshold:
      duplicate=(w,ratio);break
    if duplicate:
     removed.append({'side':side,'horizon':h,'genome_hash':k,'duplicate_of':duplicate[0][1],'overlap':duplicate[1],'reason':'REDUNDANT_SIGNAL'})
    else:
     winners.append((q,k,c,r));active.append({'side':side,'horizon':h,'genome_hash':k,'lcb95':q[0],'ev_net':q[1]})
 return {'active':active,'deleted_from_active_population':removed,'source_records_retained_for_audit':True,'overlap_threshold':threshold}
