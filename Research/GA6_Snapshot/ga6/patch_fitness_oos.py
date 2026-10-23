from pathlib import Path
p=Path('/opt/mts/ga6/fitness.py');s=p.read_text()
needle=' return 100*ev+30*ge+0.2*pf_reward+2*tail-0.5*dd'
assert s.count(needle)==1
replacement=''' base=100*ev+30*ge+0.2*pf_reward+2*tail-0.5*dd
 policy=result.get('ga6_policy_oos',{})
 # Never use validation outcomes for selection; validation is reporting only.
 if policy.get('eligible') and policy.get('train',{}).get('eligible'):
  training=policy['train']
  improvement=training.get('mean_incremental',0.)
  downside=training.get('tail_incremental',0.)
  if isfinite(improvement) and isfinite(downside):
   base+=100*improvement+30*downside
 return base'''
p.write_text(s.replace(needle,replacement))
print('Fitness adds training-only policy EV and tail; validation excluded')
