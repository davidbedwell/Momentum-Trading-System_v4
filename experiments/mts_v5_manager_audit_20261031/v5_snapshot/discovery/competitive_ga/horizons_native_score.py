"""Original Horizons sparse weighted score, with strict feature provenance.
The caller supplies causally normalized features in the original 28-feature order.
This is a score primitive, NOT an executable trading adapter.
"""
import math
STOCK=('ret5','ret20','sma20','range20','rsi14','relvol','dd252','rvpct')
MARKET=('mret5','mret20','mdd','breadth200','breadth20','mrv','breadth_vel5','breadth_vel10','breadth_accel','breadth_persist','prior_destruction','price_impulse','failed_rebound_reduction','short_trend_repair','vix','vvix','funding','credit','stress_norm','recovery_retention')
FEATURES=STOCK+MARKET

def score(genome,features):
 ids=genome['ids'];weights=genome['w']
 if len(ids)!=len(weights) or not ids:raise ValueError('invalid sparse genome')
 total=0.
 for index,weight in zip(ids,weights):
  if type(index) is not int or not 0<=index<len(FEATURES):raise ValueError('invalid feature ID')
  name=FEATURES[index]
  if name not in features:raise ValueError('missing causal normalized feature: '+name)
  value=float(features[name]);weight=float(weight)
  if not math.isfinite(value) or not math.isfinite(weight):raise ValueError('nonfinite feature or weight')
  total+=value*weight
 return total
