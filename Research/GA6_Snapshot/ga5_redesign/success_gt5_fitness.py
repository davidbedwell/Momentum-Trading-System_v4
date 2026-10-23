"""Diagnostic joint success >5% and win-rate fitness, risk-constrained."""
import math
def fitness(result):
 s=result.get('shadow',{});n=int(s.get('closed_trades') or 0)
 if n<30:return -100.0+(n/1000)
 win=float(s.get('win_rate') or 0);big=float(s.get('success_gt5_rate') or 0)
 expectancy=float(s.get('mean_net_return') or 0)
 tail=float(result.get('exit_objectives',{}).get('tail') or -1)
 dd=abs(float(result.get('mdd_diagnostic') or 0))
 if not all(map(math.isfinite,(win,big,expectancy,tail,dd))):return -1e9
 if dd>1:return -1e9
 confidence=max(0.,1.-30./n)
 return confidence*(1.5*big+0.5*win+0.5*max(-.3,min(.3,expectancy)))-0.7*dd-0.5*max(0.,-tail-.15)
