"""Versioned GA5 survivor selection: productivity first, structural diversity second."""
from dataclasses import asdict

STRUCTURAL=('entry_feature','hold_feature','exit_feature','regime_feature','sizing_feature','replace_feature','time_exit_enabled')

def structural_signature(genome):
 return tuple(getattr(genome,key) for key in STRUCTURAL)

def select(scored,cap=500,parent_cap=None):
 """scored=(fitness,genome,result); never admit unproductive candidates for novelty alone.

 The archive of all evaluated candidates is maintained separately by the caller.
 """
 if cap<1:raise ValueError('Invalid population cap')
 eligible=[item for item in scored if item[0]>0 and item[2].get('exit_objectives',{}).get('count',0)>=20]
 eligible.sort(key=lambda x:(-x[0],x[1].identity()))
 if not eligible:return [],{'eligible':0,'selected':0,'distinct_signatures':0}
 # Productivity dominates: take top 80% of available slots by fitness, then
 # fill remaining slots with highest-fitness candidates with new structures.
 slots=min(cap,len(eligible));core=eligible[:max(1,(slots*4)//5)]
 chosen=list(core);seen_ids={x[1].identity() for x in chosen}
 signatures={structural_signature(x[1]) for x in chosen}
 for item in eligible[len(core):]:
  if len(chosen)>=slots:break
  if item[1].identity() not in seen_ids and structural_signature(item[1]) not in signatures:
   chosen.append(item);seen_ids.add(item[1].identity());signatures.add(structural_signature(item[1]))
 for item in eligible[len(core):]:
  if len(chosen)>=slots:break
  if item[1].identity() not in seen_ids:
   chosen.append(item);seen_ids.add(item[1].identity());signatures.add(structural_signature(item[1]))
 return chosen,{'eligible':len(eligible),'selected':len(chosen),'distinct_signatures':len(signatures)}
