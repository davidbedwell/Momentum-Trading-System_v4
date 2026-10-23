from pathlib import Path
p=Path('/opt/mts/ga6/niche_evidence.py');s=p.read_text();a="eligible=n>=min_trades and episodes>=max(min_episodes,12) and ev>0 and lg>0 and confidence['eligible'] and confidence['robust_positive']";b="eligible=n>=min_trades and episodes>=min_episodes and ev>0 and lg>0";assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
p=Path('/opt/mts/ga6/fitness.py');s=p.read_text();a=" uncertainty=result.get('ga6_episode_uncertainty')\n if uncertainty is not None and (not uncertainty.get('eligible') or not uncertainty.get('robust_positive')):\n  return -5+min(0.,ev)\n";assert s.count(a)==1;s=s.replace(a,'');p.write_text(s)
print('Restored discovery eligibility and fitness; confidence metrics retained as diagnostics')
