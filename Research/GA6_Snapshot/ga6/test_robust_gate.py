import sys
sys.path.insert(0,'/opt/mts')
from ga6.fitness import fitness
r={'ga6_trade_metrics':{'count':100,'net_ev':.03,'geometric_log_ev':.02,'worst_5pct_mean':-.1,'profit_factor':2},'mdd_diagnostic':.2}
a=dict(r,ga6_episode_uncertainty={'eligible':True,'robust_positive':True})
b=dict(r,ga6_episode_uncertainty={'eligible':True,'robust_positive':False})
assert fitness(a)>fitness(b)
print('PASS uncertainty eligibility gate')
