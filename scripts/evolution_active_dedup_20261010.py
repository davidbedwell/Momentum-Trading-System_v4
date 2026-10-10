"""Deduplicate the active evolutionary population without erasing immutable evidence."""
import json
from scripts.evolution_safety_20261010 import overlap,atomic_json
from scripts.run_evolution_v2_20261010 import qualify
def curate(genomes,results,domains,horizons,threshold=.85):
 from scripts.audit_evolution_domains_20261010 import valid
 active=[];removed=[]
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
    dupe=next(((w,overlap(r['signal'],w[3]['signal'])) for w in winners if overlap(r['signal'],w[3]['signal'])>=threshold),None)
    if dupe:
     removed.append({'side':side,'horizon':h,'genome_hash':k,'duplicate_of':dupe[0][1],'overlap':dupe[1],'reason':'REDUNDANT_SIGNAL'})
    else:
     winners.append((q,k,c,r))
     active.append({'side':side,'horizon':h,'genome_hash':k,'lcb95':q[0],'ev_net':q[1]})
 return {'active':active,'deleted_from_active_population':removed,'source_records_retained_for_audit':True,'overlap_threshold':threshold}
