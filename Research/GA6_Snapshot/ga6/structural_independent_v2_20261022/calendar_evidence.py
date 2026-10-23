"""Fail-closed construction of aligned net-return differential matrices.
Input is a complete daily portfolio-equity record per candidate and benchmark,
not per-trade returns. Missing days/candidates are never silently zero-filled.
"""
import hashlib
import json
import numpy as np

def build_matrix(dates,candidate_daily_returns,benchmark_daily_returns,plan):
 if len(dates)<3 or len(dates)!=len(set(dates)) or list(dates)!=sorted(dates):
  raise ValueError("Calendar must be chronological and unique")
 if not isinstance(candidate_daily_returns,dict) or not candidate_daily_returns:
  raise ValueError("Missing candidate portfolio returns")
 if not isinstance(plan,dict) or plan.get('loss_differential')!='candidate_net_return_minus_benchmark_net_return':
  raise ValueError("Unregistered loss differential")
 benchmark=np.asarray(benchmark_daily_returns,dtype=float)
 if benchmark.shape!=(len(dates),) or not np.isfinite(benchmark).all():
  raise ValueError("Incomplete benchmark calendar")
 if plan.get('calendar_start')!=dates[0] or plan.get('calendar_end')!=dates[-1]:
  raise ValueError("Data dates do not match preregistration")
 identities=sorted(candidate_daily_returns)
 columns=[]
 for identity in identities:
  values=np.asarray(candidate_daily_returns[identity],dtype=float)
  if values.shape!=(len(dates),) or not np.isfinite(values).all():
   raise ValueError("Incomplete daily portfolio returns for "+identity)
  if np.any(values<=-1):raise ValueError("Impossible daily return")
  columns.append(values-benchmark)
 matrix=np.column_stack(columns)
 payload=json.dumps({'dates':list(dates),'candidates':identities,'matrix_sha256':hashlib.sha256(matrix.tobytes()).hexdigest()},sort_keys=True)
 return {'dates':list(dates),'candidate_ids':identities,'differentials':matrix,
         'evidence_fingerprint':hashlib.sha256(payload.encode()).hexdigest(),
         'calendar_sessions':len(dates),'certification':False}
