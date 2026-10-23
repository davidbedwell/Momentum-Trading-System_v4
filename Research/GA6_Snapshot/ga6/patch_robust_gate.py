from pathlib import Path
p=Path('/opt/mts/ga6/fitness.py');s=p.read_text();needle=" base=100*ev+30*ge+0.2*pf_reward+2*tail-0.5*dd";assert s.count(needle)==1;s=s.replace(needle," uncertainty=result.get('ga6_episode_uncertainty')\n if uncertainty is not None and (not uncertainty.get('eligible') or not uncertainty.get('robust_positive')):\n  return -5+min(0.,ev)\n"+needle);p.write_text(s)
print('Research fitness now requires positive episode-block lower confidence bounds')
