"""Horizons original long-only target allocation and incumbent persistence.
Consumes current-close qualified strengths, no realized future returns.
Downside/uncertainty transformations must be performed by validated upstream inputs.
"""
import math

def allocate(genome,strengths,previous=None,cap=.10):
 if genome.get('short',False):raise ValueError('short-enabled genome requires short accounting adapter')
 if genome.get('alloc') not in ('strength',):raise ValueError('allocation transform not yet validated')
 if not 0<cap<=1.:raise ValueError('invalid cap')
 previous=previous or {}
 keys=sorted(strengths)
 s={k:max(0.,float(strengths[k])) for k in keys}
 if not all(math.isfinite(v) for v in s.values()):raise ValueError('nonfinite strength')
 gross=sum(s.values())
 target={k:v/gross if gross>0 else 0. for k,v in s.items()}
 margin=float(genome['replace_margin'])
 if not 0<=margin<=1:raise ValueError('invalid replace margin')
 if sum(previous.values())>0 and gross>0:
  for k in keys:
   old=float(previous.get(k,0.))
   if old>0 and target[k]>0 and target[k]+margin>=old:
    target[k]=max(old,target[k])
  total=sum(target.values())
  if total>1:target={k:v/total for k,v in target.items()}
 # Capping leaves unallocated cash rather than silently concentrating elsewhere.
 return {k:min(cap,v) for k,v in target.items() if v>0}
