import csv,json,pathlib,math,statistics,collections
root=pathlib.Path('/home/ubuntu/Momentum-Trading-System_v4')
base=root/'Research/Runs/gen2-200-parent-20261010'
results=[json.loads(x) for x in (base/'evaluations.jsonl').open()]
children={x['offspring_id']:json.loads(x) for x in []}
children={x['offspring_id']:x for x in (json.loads(z) for z in (base/'offspring.jsonl').open())}
horizons=(1,2,3,5,7,10,15,20,63)
def metric(r):
 p=r['points'];v=[x['ev_net'] if x['ev_net'] is not None and math.isfinite(x['ev_net']) else float('-inf') for x in p]
 positive=[x>0 for x in v];longest=run=0
 for flag in positive:
  run=run+1 if flag else 0;longest=max(longest,run)
 valid=[(i,x) for i,x in enumerate(p) if math.isfinite(v[i])]
 if not valid:return None
 i=max((i for i,x in valid),key=lambda i:v[i])
 return {'offspring_id':r['offspring_id'],'side':children[r['offspring_id']]['side'],'genome_hash':r['genome_hash'],'parent_indices':children[r['offspring_id']]['parent_indices'],'families':str([x[0] for x in children[r['offspring_id']]['chromosomes']]),'ev_net':v[i],'lcb95':p[i]['lcb95'],'effective_n':p[i]['effective_n'],'best_horizon':p[i]['horizon'],'positive_fraction':sum(positive)/len(horizons),'positive_run':longest,'positive_count':sum(positive),'horizon_count':len(horizons),'median_positive_ev':statistics.median(x for x in v if x>0) if any(positive) else 0,'n_best':p[i]['n'],'cvar5_best':p[i]['cvar5'],'lcb_positive_count':sum(x['lcb95']>0 for x in p),'horizon_63_ev':p[-1]['ev_net']}
rows=[metric(x) for x in results if x['status']=='EVALUATED_UNCERTIFIED'];rows=[r for r in rows if r]
# Gen1 priority: four-dimensional Pareto EV, LCB, positive fraction, positive run.
dims=('ev_net','lcb95','positive_fraction','positive_run')
def dominates(a,b):return all(a[k]>=b[k] for k in dims) and any(a[k]>b[k] for k in dims)
remaining=rows[:];front=0
while remaining:
 front+=1;layer=[r for r in remaining if not any(dominates(s,r) for s in remaining if s is not r)]
 for r in layer:r['pareto_front']=front
 remaining=[r for r in remaining if r not in layer]
rows.sort(key=lambda r:(r['pareto_front'],-r['positive_run'],-r['positive_fraction'],-r['lcb95'],-r['ev_net'],r['offspring_id']))
for i,r in enumerate(rows,1):r['overall_priority']=i
with (base/'gen2_gen1_criteria_ranking.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={'method':'Gen1 exploratory 4D Pareto; same nine horizons; uncertified','evaluated':len(results),'ranked':len(rows),'pareto_front1':sum(r['pareto_front']==1 for r in rows),'best_ev_positive':sum(r['ev_net']>0 for r in rows),'best_lcb_positive':sum(r['lcb95']>0 for r in rows),'all_nine_positive':sum(r['positive_count']==9 for r in rows),'lcb_positive_all_nine':sum(r['lcb_positive_count']==9 for r in rows),'positive_horizons_distribution':dict(sorted(collections.Counter(r['positive_count'] for r in rows).items())),'best_horizon_distribution':dict(sorted(collections.Counter(r['best_horizon'] for r in rows).items())),'side_distribution':dict(collections.Counter(r['side'] for r in rows)),'top10':[dict((k,r[k]) for k in ('overall_priority','offspring_id','pareto_front','ev_net','lcb95','effective_n','best_horizon','positive_count','positive_run','lcb_positive_count')) for r in rows[:10]]}
(base/'gen2_gen1_criteria_summary.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
