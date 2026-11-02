"""Auditable origin and P&L attribution across manager stages."""
from dataclasses import dataclass
from collections import defaultdict,Counter

FAMILIES=('NICHE','NO_NICHE','GA4','HORIZONS')
EVENTS=('QUALIFIED','SELECTED','ORDERED','FILLED','CLOSED')

@dataclass(frozen=True)
class Event:
 date:str
 ticker:str
 chromosome_id:str
 family:str
 event:str
 niche:str=''
 net_profit:float=0.
 shadow:bool=False
 def __post_init__(self):
  if self.family not in FAMILIES or self.event not in EVENTS:raise ValueError('invalid event')
  if self.shadow and self.event in ('ORDERED','FILLED'):raise ValueError('shadow fill is not a real fill')

def summarize(events):
 families={f:Counter() for f in FAMILIES}
 niches=defaultdict(Counter)
 for e in events:
  key=e.event.lower()+('_shadow' if e.shadow else '')
  families[e.family][key]+=1
  if e.event=='CLOSED':families[e.family]['shadow_profit' if e.shadow else 'realized_profit']+=e.net_profit
  if e.family=='NICHE':niches[e.niche][key]+=1
 return {'families':{k:dict(v) for k,v in families.items()},'niches':{k:dict(v) for k,v in niches.items()}}
