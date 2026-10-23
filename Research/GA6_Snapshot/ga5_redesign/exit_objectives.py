"""Optional exit-policy research objectives; never used as future-aware signals."""
from math import isfinite
from statistics import mean
OBJECTIVES=('expectancy','capture','giveback','adverse','tail','efficiency')
def metrics(trades):
 rows=[t for t in trades if all(k in t for k in ('entry','exit','net_return'))]
 if not rows:return {'count':0,'status':'INSUFFICIENT_TRADES'}
 r=sorted(float(t['net_return']) for t in rows)
 for v in r:
  if not isfinite(v):raise ValueError('Nonfinite return')
 cap=[];give=[];adverse=[];eff=[]
 for t in rows:
  entry=float(t['entry']);exit_=float(t['exit']);mfe=max(0.,float(t.get('mfe',0)));mae=min(0.,float(t.get('mae',0)))
  if entry<=0 or exit_<=0 or not all(isfinite(x) for x in (mfe,mae)):raise ValueError('Invalid trade')
  realized=exit_/entry-1
  if mfe>0:cap.append(max(0.,min(1.,realized/mfe)))
  give.append(-max(0.,mfe-realized))
  adverse.append(mae)
  eff.append(float(t['net_return'])/max(1,int(t.get('sessions',1))))
 n=max(1,int(len(r)*.05))
 return {'count':len(rows),'status':'DIAGNOSTIC_ONLY','expectancy':mean(r),'capture':mean(cap) if cap else None,'capture_coverage':len(cap),'giveback':mean(give),'adverse':mean(adverse),'tail':mean(r[:n]),'efficiency':mean(eff)}
def dominates(a,b,keys=OBJECTIVES):
 if not a.get('count') or not b.get('count'):return False
 pairs=[(a.get(k),b.get(k)) for k in keys]
 if any(x is None or y is None for x,y in pairs):return False
 return all(x>=y for x,y in pairs) and any(x>y for x,y in pairs)
def pareto_front(candidates):
 return [i for i,a in enumerate(candidates) if not any(dominates(b,a) for j,b in enumerate(candidates) if i!=j)]
def calmar(cagr,mdd,minimum_drawdown=.01):
 if not all(isfinite(float(x)) for x in (cagr,mdd)):raise ValueError('Invalid portfolio metric')
 return float(cagr)/max(abs(float(mdd)),minimum_drawdown)
