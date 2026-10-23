"""Convert complete daily NAV histories into aligned net portfolio returns."""
import numpy as np
from ga6.structural_independent_v2_20261022.calendar_evidence import build_matrix

def nav_to_returns(nav,starting_cash):
 if not isinstance(starting_cash,(int,float)) or starting_cash<=0:
  raise ValueError("Invalid starting cash")
 if not nav:raise ValueError("Missing daily NAV")
 dates=[str(day)[:10] for day,_ in nav]
 if dates!=sorted(set(dates)):raise ValueError("Unordered or duplicate NAV sessions")
 values=np.asarray([value for _,value in nav],dtype=float)
 if not np.isfinite(values).all() or np.any(values<=0):
  raise ValueError("Invalid NAV")
 previous=np.concatenate(([float(starting_cash)],values[:-1]))
 return dates,(values/previous-1).tolist()

def from_replays(replays,benchmark_nav,starting_cash,plan):
 if not replays:raise ValueError("Missing replay histories")
 benchmark_dates,benchmark_returns=nav_to_returns(benchmark_nav,starting_cash)
 candidates={}
 for candidate_id,result in replays.items():
  if result.get('status')!='GUARDED_RESEARCH_ONLY':
   raise ValueError("Noncanonical portfolio replay")
  if 'calendar_nav' not in result:raise ValueError("Replay missing full NAV history")
  dates,returns=nav_to_returns(result['calendar_nav'],starting_cash)
  if dates!=benchmark_dates:raise ValueError("Misaligned portfolio sessions")
  candidates[candidate_id]=returns
 return build_matrix(benchmark_dates,candidates,benchmark_returns,plan)
