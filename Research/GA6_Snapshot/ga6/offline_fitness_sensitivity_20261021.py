import json,collections,math,statistics
from pathlib import Path
src=Path('/opt/mts/ga6/runs/ga6_production_200_v1/all_evaluations.jsonl')
rows=[]
for line in src.open():
 x=json.loads(line);m=x['result'].get('ga6_trade_metrics',{})
 vals=[m.get('net_ev'),m.get('geometric_log_ev'),m.get('worst_5pct_mean'),x['result'].get('mdd_diagnostic')]
 if not all(isinstance(v,(int,float)) and math.isfinite(v) for v in vals):continue
 ev,ge,tail,dd=vals
 if m['count']<50 or ev<=0 or ge<=0:continue
 x['_metrics']=(ev,ge,tail,abs(dd));rows.append(x)
scenarios={'baseline_proxy':(2,.5),'moderate':(30,20),'strong':(60,40),'very_strong':(100,75)}
by=collections.defaultdict(list)
for x in rows:by[x['generation']].append(x)
for gen in sorted(by):
 a=by[gen];out={'generation':gen,'eligible':len(a),'population_median_tail':statistics.median(x['_metrics'][2] for x in a)}
 for label,(tw,dw) in scenarios.items():
  winner=max(a,key=lambda x:100*x['_metrics'][0]+30*x['_metrics'][1]+tw*x['_metrics'][2]-dw*x['_metrics'][3])
  ev,ge,tail,dd=winner['_metrics']
  out[label]={'id':winner['chromosome_id'][:12],'niche':winner['genome']['niche'],'ev':round(ev,4),'tail':round(tail,4),'mdd':round(dd,4),'cagr':winner['result'].get('cagr_diagnostic'),'trades':winner['result']['ga6_trade_metrics']['count'],'stop':winner['genome']['stop_loss']}
 print(json.dumps(out))
