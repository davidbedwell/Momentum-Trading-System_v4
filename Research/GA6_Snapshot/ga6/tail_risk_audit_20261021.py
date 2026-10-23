import json,statistics,collections
from pathlib import Path
p=Path('/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl')
by=collections.defaultdict(list)
for line in p.open():
 x=json.loads(line);by[x['generation']].append(x)
for gen in sorted(by):
 a=by[gen];top=max(a,key=lambda x:x['fitness']);r=top['result'];m=r['ga6_trade_metrics'];v=[x['result']['ga6_trade_metrics']['worst_5pct_mean'] for x in a if isinstance(x['result']['ga6_trade_metrics'].get('worst_5pct_mean'),(int,float))];print(json.dumps({'generation':gen,'population_tail_median':statistics.median(v),'population_tail_mean':statistics.mean(v),'population_tail_min':min(v),'population_tail_max':max(v),'best':{'id':top['chromosome_id'],'niche':top['genome']['niche'],'fitness':top['fitness'],'tail':m['worst_5pct_mean'],'count':m['count'],'stop_loss':top['genome']['stop_loss'],'trailing_stop':top['genome']['trailing_stop'],'max_hold_sessions':top['genome']['max_hold_sessions'],'time_exit_enabled':top['genome']['time_exit_enabled'],'max_weight':top['genome']['max_weight'],'cagr':r.get('cagr_diagnostic'),'mdd':r.get('mdd_diagnostic'),'policy_oos':r.get('ga6_policy_oos')}},default=str))
