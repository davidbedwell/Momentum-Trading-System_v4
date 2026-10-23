"""Fresh GA6-only evolvable exit/reentry policy genes; no GA5 elite imports."""
from dataclasses import dataclass,asdict,replace
from hashlib import sha256
import json
from ga6.prospective_policy import Policy
@dataclass(frozen=True)
class ExitGenes:
 trigger:float
 recovery:float
 min_wait:int
 max_wait:int
 def valid(self):
  return 0.01<=self.trigger<=0.40 and 0<=self.recovery<=1 and 1<=self.min_wait<=self.max_wait<=63
 def policy(self):
  if not self.valid():raise ValueError('invalid genes')
  return Policy(self.trigger,self.recovery,self.min_wait,self.max_wait)
 def identity(self):return sha256(json.dumps(asdict(self),sort_keys=True).encode()).hexdigest()
def fresh(rng):
 return ExitGenes(round(rng.uniform(.02,.25),4),round(rng.random(),4),rng.randint(1,5),rng.randint(6,40))
def mutate(g,rng):
 field=rng.choice(('trigger','recovery','min_wait','max_wait'))
 if field in ('trigger','recovery'):
  delta=rng.choice((-.05,-.02,-.01,.01,.02,.05));value=round(max(.01 if field=='trigger' else 0.,min(.40 if field=='trigger' else 1.,getattr(g,field)+delta)),4)
 else:value=max(1,min(63,getattr(g,field)+rng.choice((-5,-2,-1,1,2,5))))
 x=replace(g,**{field:value})
 if x.min_wait>x.max_wait:x=replace(x,max_wait=x.min_wait)
 return x
