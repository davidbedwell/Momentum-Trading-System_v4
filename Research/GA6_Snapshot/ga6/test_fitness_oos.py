import sys
sys.path.insert(0,'/opt/mts')
from ga6.fitness import fitness
base={'ga6_trade_metrics':{'count':100,'net_ev':.03,'geometric_log_ev':.02,'worst_5pct_mean':-.1,'profit_factor':2},'mdd_diagnostic':.2}
a=dict(base);a['ga6_policy_oos']={'eligible':True,'train':{'eligible':True,'mean_incremental':.05,'tail_incremental':-.02},'validation':{'mean_incremental':-.5}}
b=dict(base);b['ga6_policy_oos']={'eligible':True,'train':{'eligible':True,'mean_incremental':.05,'tail_incremental':-.02},'validation':{'mean_incremental':.5}}
assert fitness(a)==fitness(b),'validation leakage'
assert fitness(a)!=fitness(base),'training policy not incorporated'
print('PASS policy fitness uses training only; validation cannot influence selection')
