"""Checkpoint progress using best statistically positive EV/LCB by horizon."""
import math

def frontier(results, horizons):
 out={str(h):{'best_ev_net':None,'best_lcb95':None,'qualified_count':0} for h in horizons}
 for r in results:
  if r.get('status')!='EVALUATED_UNCERTIFIED':continue
  for p in r.get('points',[]):
   h=str(p.get('horizon'))
   if h not in out:continue
   ev,lo,n=p.get('ev_net'),p.get('lcb95'),p.get('effective_n')
   if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (ev,lo,n)):continue
   if n<30 or ev<=0 or lo<=0:continue
   x=out[h];x['qualified_count']+=1
   if x['best_ev_net'] is None or ev>x['best_ev_net']:x['best_ev_net']=float(ev)
   if x['best_lcb95'] is None or lo>x['best_lcb95']:x['best_lcb95']=float(lo)
 return out

def checkpoint(history,front,gen,step=25,window=100,patience=2,tolerance=1e-12):
 if gen==0 or gen%step:return None
 old=[x for x in history if x['generation']<=gen-window]
 previous=old[-1]['frontier'] if old else None
 improvements=[]
 if previous:
  for h,current in front.items():
   prior=previous.get(h,{})
   if current['best_ev_net'] is not None and current['best_lcb95'] is not None:
    if (prior.get('best_ev_net') is None or current['best_ev_net']>prior['best_ev_net']+tolerance) and (prior.get('best_lcb95') is None or current['best_lcb95']>prior['best_lcb95']+tolerance):improvements.append(h)
 prev=history[-1]['stale_checkpoints'] if history else 0
 stale=0 if previous is None or improvements else prev+1
 return {'generation':gen,'frontier':front,'improved_horizons':improvements,'stale_checkpoints':stale,'rolling_generations':window,'stop':previous is not None and stale>=patience}
