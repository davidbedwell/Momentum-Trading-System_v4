"""Niche-specific entry+hold+exit diagnostic fitness; shadow trades only, no portfolio fitness.
No arbitrary horizon, no scaling. Future-aware validation prohibited.
"""
import math
def fitness(result):
 s=result.get('shadow',{});n=int(s.get('closed_trades') or 0)
 if n<50:return -100+(n/1000)
 big=float(s.get('success_gt5_rate') or 0);win=float(s.get('win_rate') or 0)
 ev=float(s.get('mean_net_return') or 0);ex=result.get('exit_objectives',{})
 tail=float(ex.get('tail') or -1);adverse=float(ex.get('adverse') or -1)
 if not all(map(math.isfinite,(big,win,ev,tail,adverse))):return -1e9
 if ev<=0:return -5+ev
 confidence=max(0.,1.-50/n)
 return confidence*(3*big+win+min(.3,ev))-2*max(0.,-tail-.08)-max(0.,-adverse-.06)
