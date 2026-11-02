"""Synthetic routing benchmark: counts native calls, not trading returns."""
import json,time
from pathlib import Path
from discovery.competitive_ga.hierarchical_search import RoutedCandidate,screen_all
from discovery.competitive_ga.adaptive_search import SearchPolicy,search_session

def run():
 bank=[RoutedCandidate('n'+str(i),'GA6','NICHE-0001') for i in range(100)]
 bank += [RoutedCandidate('u'+str(i),'GA6') for i in range(100)]
 bank += [RoutedCandidate('g'+str(i),'GA4') for i in range(100)]
 bank += [RoutedCandidate('h'+str(i),'HORIZONS') for i in range(100)]
 rows={str(i):{'close':10} for i in range(10)}
 calls=[0]
 def native(c,r,h,t):
  calls[0]+=1
  return ('ENTER',.1) if c.chromosome_id=='n0' else ('NO_ENTRY',0)
 def niche(*a):return 'NICHE-0001'
 def gate(*a):return True
 t=time.perf_counter()
 for day in range(10):screen_all(rows,bank,niche,gate,native,day)
 exhaustive_calls=calls[0];exhaustive_time=time.perf_counter()-t
 calls[0]=0;t=time.perf_counter()
 samples=[]
 for day in range(10):
  x=search_session(rows,bank,niche,gate,native,day,day,SearchPolicy(5,5))
  samples.append(x['counts'])
 adaptive_calls=calls[0];adaptive_time=time.perf_counter()-t
 report={'status':'SYNTHETIC_ROUTING_ONLY_NOT_MARKET_REPLAY','stocks':10,'sessions':10,'bank_count':400,'exhaustive_native_calls':exhaustive_calls,'adaptive_native_calls':adaptive_calls,'call_reduction_fraction':1-adaptive_calls/exhaustive_calls,'exhaustive_wall_seconds':exhaustive_time,'adaptive_wall_seconds':adaptive_time,'shadow_sessions':sum(s['full_shadow_audit'] for s in samples),'expanded_sessions':sum(s['expanded'] for s in samples),'limitations':'Synthetic constant decisions; no real chromosome grammar, market features, portfolio returns, or calibrated speed extrapolation.'}
 out=Path('/opt/mts/synthetic-market-lab/reports/adaptive_routing_microbenchmark.json');out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,indent=2))
 return report
if __name__=='__main__':print(json.dumps(run(),indent=2))
