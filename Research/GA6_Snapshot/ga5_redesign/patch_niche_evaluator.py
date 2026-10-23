"""Install niche-conditional entry gate while leaving exit management intact."""
from pathlib import Path
p=Path('/opt/mts/ga5_redesign/guarded_evaluator.py');s=p.read_text();old='annual_cash_yield=None):';new='annual_cash_yield=None,niche_labels=None):';assert old in s or new in s;s=s.replace(old,new)
old='  for t,r in rows.items():\n   p=positions.get(t,PositionState())';new='  for t,r in rows.items():\n   p=positions.get(t,PositionState())';assert old in s
old='   elif not p.shares and action=="ENTER":entries.append((t,weight,f[genome.entry_feature]))';new='   elif not p.shares and action=="ENTER" and (niche_labels is None or niche_labels.get((ds,t))==genome.niche):entries.append((t,weight,f[genome.entry_feature]))';assert old in s or new in s;s=s.replace(old,new)
# Reject missing labels when niche conditioning requested.
needle=' prepared=frame if isinstance(frame,PreparedSessions) else PreparedSessions(frame)';insert=' prepared=frame if isinstance(frame,PreparedSessions) else PreparedSessions(frame)\n if niche_labels is not None and not prepared.membership_keys.issubset(niche_labels):raise ValueError("Incomplete niche label coverage")';assert needle in s or insert in s;s=s.replace(needle,insert);p.write_text(s);print('Niche entry gating patched')
