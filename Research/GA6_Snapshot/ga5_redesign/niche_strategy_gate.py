"""Research-only time-t niche gate for GA5 strategy candidates.
No future outcome inputs. Memory is frozen per experiment snapshot.
"""
import json
from pathlib import Path
import numpy as np

class NicheStrategyGate:
 def __init__(self,memory_path,allowed=None):
  self.path=Path(memory_path)
  memory=json.loads(self.path.read_text())
  self.ids=tuple(memory['ids']);self.features=tuple(memory['features'])
  self.centers=np.asarray(memory['centers'],dtype=float)
  self.median=np.asarray(memory['median'],dtype=float)
  self.scale=np.asarray(memory['scale'],dtype=float)
  if self.centers.shape!=(len(self.ids),len(self.features)) or np.any(self.scale<=0):raise ValueError('Invalid frozen niche memory')
  self.allowed=None if allowed is None else frozenset(allowed)
  if self.allowed is not None and not self.allowed.issubset(self.ids):raise ValueError('Unknown niche ID')
 def recognize(self,features_at_t):
  values=np.asarray([features_at_t[k] for k in self.features],dtype=float)
  if not np.isfinite(values).all():return None
  z=np.clip((values-self.median)/self.scale,-5,5)
  distances=np.linalg.norm(self.centers-z,axis=1)
  i=int(np.argmin(distances))
  return {'niche':self.ids[i],'distance':float(distances[i]),'trade_eligible':self.allowed is None or self.ids[i] in self.allowed}
 def register_new_memory(self,memory_path):
  """Return a new immutable snapshot gate; never mutate a live evaluation."""
  return NicheStrategyGate(memory_path,allowed=self.allowed)
