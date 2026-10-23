from pathlib import Path
root=Path('/opt/mts/ga6')
p=root/'fast_portfolio_evaluator_20261021.py'
s=p.read_text()
needle=" stats={'completed_trades':count,'win_rate':wins/count if count else None,"
assert needle in s
s=s.replace(needle,""" returns=[pnl/equity for pnl,equity,_ in completed_positions]
 ev=sum(returns)/count if count else None
 variance=sum((x-ev)**2 for x in returns)/(count-1) if count>1 else None
 se=(variance/count)**.5 if variance is not None else None
 stats={'net_ev_standard_error':se,'net_ev_lower_confidence_95':ev-1.96*se if se is not None else None,
        'losing_trades':sum(x<0 for x in returns),
        'completed_trades':count,'win_rate':wins/count if count else None,""",1)
compile(s,str(p),'exec');p.write_text(s)
q=root/'portfolio_pareto_20261021.py'
q.write_text('''"""GA6 EV-first discovery: conservative realized EV fitness; no CAGR/MDD selection."""
from math import isfinite
MIN_TRADES=30
def fitness(r):
 m=r.get('ga6_completed_position_metrics',{})
 n=m.get('completed_trades',0)
 lcb=m.get('net_ev_lower_confidence_95')
 if n<MIN_TRADES or lcb is None or not isfinite(lcb):
  return -100.
 return float(lcb)
def rank_scored(scored):
 return sorted(scored,key=lambda x:(-x[0],-x[2].get('ga6_completed_position_metrics',{}).get('completed_trades',0),x[1].identity()))
''')
compile(q.read_text(),str(q),'exec')
runner=root/'production_portfolio_20261021.py'
r=runner.read_text()
r=r.replace("scored[0][0]>best['fitness']","scored[0][0]>best['fitness']")
r=r.replace("'architecture':'GA6 EV-led niche-protected evolutionary population'","'architecture':'GA6 conservative completed-position EV fitness; niche-protected evolutionary population'")
runner.write_text(r)
print('EV_FITNESS_INSTALLED_AND_COMPILED')
