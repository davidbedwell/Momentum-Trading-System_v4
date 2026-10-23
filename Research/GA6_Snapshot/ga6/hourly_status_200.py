import json,sqlite3,subprocess,datetime
from pathlib import Path
p=Path('/opt/mts/ga6/runs/ga6_production_200_v1')
status=subprocess.run(['systemctl','is-active','mts-ga6-production-200.service'],capture_output=True,text=True).stdout.strip()
r={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'service':status,'checkpoint_present':(p/'checkpoint_unified.json').exists(),'population':200,'workers':8}
if (p/'checkpoint_unified.json').exists():
 s=json.loads((p/'checkpoint_unified.json').read_text());h=s.get('history',[]);last=h[-1] if h else {}
 r.update(generation=s.get('generation'),completed_evaluations=s.get('generation',0)*s.get('population',200),unique_chromosomes_last_generation=last.get('unique'),gene_patterns_last_generation=last.get('distinct_gene_patterns'),niches_represented=last.get('niches_represented'),niche_counts=last.get('niche_counts'),niche_eligible_counts=last.get('niche_eligible_counts'),fitness_best=last.get('best_ever_fitness'),fitness_mean=last.get('fitness_mean'),fitness_median=last.get('fitness_median'),exit_pareto_count=last.get('exit_pareto_count'),exit_metric_eligible=last.get('exit_metric_eligible'),next_population_diversity=last.get('next_population_diversity'))
 best=s.get('best') or {};m=(best.get('result') or {}).get('ga6_trade_metrics',{});r['best_quality']={'trade_count':m.get('count'),'net_ev':m.get('net_ev'),'win_rate':m.get('win_rate'),'profit_factor':m.get('profit_factor'),'worst_5pct_mean':m.get('worst_5pct_mean'),'mean_sessions_proxy':None,'fitness':best.get('fitness')}
 if len(h)>1:r['change_since_previous_generation']={'best_fitness':last.get('best_ever_fitness',0)-h[-2].get('best_ever_fitness',0),'gene_patterns':last.get('distinct_gene_patterns',0)-h[-2].get('distinct_gene_patterns',0)}
if (p/'production.log').exists():r['log_tail']=(p/'production.log').read_text(errors='replace').splitlines()[-4:]
print(json.dumps(r,default=str))
