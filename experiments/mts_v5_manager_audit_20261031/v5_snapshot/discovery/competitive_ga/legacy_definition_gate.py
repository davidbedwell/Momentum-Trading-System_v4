"""Parse frozen legacy definitions without fabricating executable decisions."""
import json
from dataclasses import dataclass

@dataclass(frozen=True)
class ParsedLegacy:
 family:str
 strategy_key:str
 payload:object
 horizon:int|None

def parse(strategy):
 if strategy.family not in ('GA4','HORIZONS'):raise ValueError('unsupported family')
 payload=json.loads(strategy.definition)
 if strategy.family=='GA4':
  if not isinstance(payload,list) or not payload:raise ValueError('invalid GA4 rules')
  if not all(isinstance(x,list) and len(x)==2 and isinstance(x[1],dict) for x in payload):raise ValueError('invalid GA4 rule shape')
  horizon=int(strategy.horizon) if strategy.horizon else None
 else:
  if not isinstance(payload,dict) or not {'ids','w','qual'}.issubset(payload):raise ValueError('invalid Horizons genome')
  if len(payload['ids'])!=len(payload['w']):raise ValueError('feature weight mismatch')
  horizon=int(strategy.horizon) if strategy.horizon else None
 return ParsedLegacy(strategy.family,strategy.chromosome_id,payload,horizon)
