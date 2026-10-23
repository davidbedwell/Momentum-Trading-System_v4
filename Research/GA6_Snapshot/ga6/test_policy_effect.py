import sys
sys.path.insert(0,'/opt/mts')
from ga6.fitness import fitness
base={'ga6_trade_metrics':{'count':100,'net_ev':.03,'geometric_log_ev':.02,'worst_5pct_mean':-.1,'profit_factor':2},'mdd_diagnostic':.2}
strong=dict(base,ga6_policy_oos={'eligible':True,'train':{'eligible':True,'mean_incremental':.03,'tail_incremental':-.01},'validation':{'mean_incremental':-.99}})
weak=dict(base,ga6_policy_oos={'eligible':True,'train':{'eligible':True,'mean_incremental':-.03,'tail_incremental':-.15},'validation':{'mean_incremental':.99}})
assert fitness(strong)>fitness(weak)
assert fitness(strong)>fitness(base)>fitness(weak)
print('PASS profitable training policy favored; losing training policy penalized')
