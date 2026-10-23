import json,collections,statistics
from pathlib import Path
p=Path('/opt/mts/ga6/runs/ga6_portfolio_production_fresh_20261021/all_evaluations.jsonl')
rows=[]
for line in p.open():
 try:rows.append(json.loads(line))
 except json.JSONDecodeError:pass
gen=max(x['generation'] for x in rows)
latest=[x for x in rows if x['generation']==gen]
latest.sort(key=lambda x:x['fitness'],reverse=True)
best=max(rows,key=lambda x:x['fitness'])
print(json.dumps({'generation':gen,'completed_evaluations':len(rows),'latest_population':len(latest),'latest_mean_fitness':statistics.mean(x['fitness'] for x in latest),'latest_median_fitness':statistics.median(x['fitness'] for x in latest),'latest_positive_cagr':sum(x['result']['cagr_diagnostic']>0 for x in latest),'latest_top_5':[{'id':x['chromosome_id'][:12],'niche':x['origin_niche'],'fitness_cagr_pct':round(x['fitness']*100,3),'cagr_pct':round(x['result']['cagr_diagnostic']*100,3),'mdd_pct':round(x['result']['mdd_diagnostic']*100,3),'buys':x['result']['signal_trace']['executed_buys'],'sells':x['result']['signal_trace']['executed_sells'],'turnover':x['result'].get('ga6_portfolio_diagnostics',{}).get('annualized_two_way_turnover')} for x in latest[:5]],'best_ever':{'id':best['chromosome_id'][:12],'generation':best['generation'],'cagr_pct':round(best['result']['cagr_diagnostic']*100,3),'mdd_pct':round(best['result']['mdd_diagnostic']*100,3)},'ev':'not_calculated_in_fast_evaluator'}))
