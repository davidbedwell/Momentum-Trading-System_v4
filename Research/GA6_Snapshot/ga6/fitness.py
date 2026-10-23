"""GA6 EV-led selection; independent of GA5 fitness."""
from math import isfinite

def fitness(result):
 m=result['ga6_trade_metrics'];n=m['count']
 if n<50:return -100+n/1000
 ev=m['net_ev'];ge=m['geometric_log_ev']
 if ev is None or ge is None or not isfinite(ev) or not isfinite(ge) or ev<=0 or ge<=0:return -10+(ev or 0)
 tail=m['worst_5pct_mean']
 pf=m['profit_factor']
 pf_reward=min(3.,pf) if pf is not None and isfinite(pf) else 3.
 dd=abs(float(result['mdd_diagnostic']))
 base=100*ev+30*ge+0.2*pf_reward+2*tail-0.5*dd
 policy=result.get('ga6_policy_oos',{})
 # Never use validation outcomes for selection; validation is reporting only.
 if policy.get('eligible') and policy.get('train',{}).get('eligible'):
  training=policy['train']
  improvement=training.get('mean_incremental',0.)
  downside=training.get('tail_incremental',0.)
  if isfinite(improvement) and isfinite(downside) and improvement>0:
   base+=100*improvement+30*downside
 return base
