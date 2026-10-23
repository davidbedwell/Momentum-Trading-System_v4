import sys,random
sys.path[:0]=['/opt/mts','/opt/mts/ga5_redesign']
from ga6.fitness import fitness
from ga6.breeder import breed_ga6
from ga5_redesign.niche_seeds import initial
from ga5_redesign.optimizer_v3 import NICHES

def test_ev_beats_winrate():
 def r(ev,log,pf,tail):return {'ga6_trade_metrics':{'count':100,'net_ev':ev,'geometric_log_ev':log,'profit_factor':pf,'worst_5pct_mean':tail},'mdd_diagnostic':-.1}
 assert fitness(r(.036,.031,2.5,-.04))>fitness(r(-.009,-.011,.7,-.1))

def test_fresh_niche_breeding():
 scored=[(0.,initial(n),{}) for n in NICHES]
 out,stats=breed_ga6(scored,random.Random(6106),52)
 assert len(out)==52 and stats['niches_represented']==13
 assert len({g.identity() for g in out})==52
