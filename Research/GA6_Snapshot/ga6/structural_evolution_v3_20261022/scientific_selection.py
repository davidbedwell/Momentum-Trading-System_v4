"""Fail-closed GA6 scientific eligibility and deterministic three-objective Pareto."""
from math import isfinite
from collections import defaultdict

def eligible(evidence,criteria):
 """Explicit evidence only: never infer missing tail/stability from positive fitness."""
 required=('completed_trades','net_ev_lcb_adjusted','trades_per_year','capital_time_efficiency','expected_shortfall','max_drawdown','stability_fraction','multiplicity_verified','costs_verified','oos_verified')
 missing=[k for k in required if k not in evidence]
 if missing:return False,('missing:'+','.join(missing),)
 if any(not isinstance(evidence[k],(int,float)) or not isfinite(evidence[k]) for k in required[:7]):return False,('nonfinite',)
 reasons=[]
 checks=(('completed_trades',lambda x:x>=criteria['min_trades']),('net_ev_lcb_adjusted',lambda x:x>criteria['min_adjusted_ev']),('trades_per_year',lambda x:x>=criteria['min_trades_per_year']),('expected_shortfall',lambda x:x>=-criteria['max_expected_shortfall']),('max_drawdown',lambda x:x>=-criteria['max_drawdown']),('stability_fraction',lambda x:x>=criteria['min_stability']))
 for name,predicate in checks:
  if not predicate(evidence[name]):reasons.append(name)
 for flag in ('multiplicity_verified','costs_verified','oos_verified'):
  if evidence[flag] is not True:reasons.append(flag)
 return not reasons,tuple(reasons)

def dominates(a,b):
 return all(x>=y for x,y in zip(a,b)) and any(x>y for x,y in zip(a,b))

def truncate(scored,limit):
 """scored: (identity, evidence) pairs already passing hard gates."""
 if limit<1:raise ValueError('limit must be positive')
 vals={ident:(float(e['net_ev_lcb_adjusted']),float(e['capital_time_efficiency']),float(e['expected_shortfall'])) for ident,e in scored}
 if len(vals)!=len(scored):raise ValueError('Duplicate identity')
 if any(not all(isfinite(x) for x in v) for v in vals.values()):raise ValueError('Nonfinite Pareto evidence')
 remaining=set(vals);selected=[]
 while remaining and len(selected)<limit:
  front=sorted(k for k in remaining if not any(dominates(vals[other],vals[k]) for other in remaining if other!=k))
  if len(front)<=limit-len(selected):selected.extend(front);remaining.difference_update(front);continue
  distance={k:0. for k in front}
  for j in range(3):
   ordered=sorted(front,key=lambda k:(vals[k][j],k));lo=vals[ordered[0]][j];hi=vals[ordered[-1]][j]
   if hi==lo:continue
   distance[ordered[0]]=float('inf');distance[ordered[-1]]=float('inf')
   for i in range(1,len(ordered)-1):distance[ordered[i]]+=(vals[ordered[i+1]][j]-vals[ordered[i-1]][j])/(hi-lo)
  selected.extend(sorted(front,key=lambda k:(-distance[k],k))[:limit-len(selected)])
  break
 return selected

def niche_archive(scored,criteria,per_niche=10):
 by=defaultdict(list);rejected=[]
 for ident,niche,evidence in scored:
  passed,reasons=eligible(evidence,criteria)
  if passed:by[niche].append((ident,evidence))
  else:rejected.append((ident,niche,reasons))
 return {n:truncate(items,per_niche) for n,items in sorted(by.items())},rejected
