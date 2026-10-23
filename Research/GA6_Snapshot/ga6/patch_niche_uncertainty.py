from pathlib import Path
p=Path('/opt/mts/ga6/niche_evidence.py');s=p.read_text();a="  eligible=n>=min_trades and episodes>=min_episodes and ev>0 and lg>0";b="  from ga6.episode_uncertainty import assess\n  confidence=assess(ts)\n  eligible=n>=min_trades and episodes>=max(min_episodes,12) and ev>0 and lg>0 and confidence['eligible'] and confidence['robust_positive']";assert s.count(a)==1;s=s.replace(a,b)
a="'eligible':eligible,'win_rate'";b="'eligible':eligible,'uncertainty':confidence,'win_rate'";assert s.count(a)==1;s=s.replace(a,b);p.write_text(s)
print('Each niche now requires episode-aware positive EV/log-EV confidence')
