import sys,random
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from niche_seeds import initial
from optimizer_v3 import NICHES
from evolution_controls import breed_next
from niche_portfolio_breeder_v1 import breed_niche_portfolio
r=random.Random(1700)
seeds=[initial(n) for n in NICHES]
pop,_=breed_next([(0.,g,{}) for g in seeds],r,52)
scored=[(0.,g,dict(cagr_diagnostic=.08+(i%7)*.01,mdd_diagnostic=-.12-(i%5)*.03,fills=10,exit_objectives=dict(expectancy=10.))) for i,g in enumerate(pop)]
children,stats=breed_niche_portfolio(scored,r,52)
assert len(children)==52 and len(set(g.identity() for g in children))==52
assert len({g.niche for g in children})==13
print('PASS',stats)
