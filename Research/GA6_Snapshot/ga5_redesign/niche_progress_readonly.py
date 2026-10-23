import json,collections,statistics
p='/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/all_evaluations.jsonl'
seen={}; gen=collections.defaultdict(list)
for line in open(p):
 x=json.loads(line);seen[x['chromosome_id']]=x;gen[x['generation']].append(x)
print('GENERATIONS',max(gen),'UNIQUE',len(seen),'EVALUATIONS',sum(map(len,gen.values())))
for k in [1,20,50,80,100,max(gen)]:
 if k not in gen:continue
 rows=gen[k];valid=[x for x in rows if x['result'].get('cagr_diagnostic') is not None]
 top=max(valid,key=lambda x:x['result']['cagr_diagnostic'])
 fit=max(rows,key=lambda x:x['fitness'])
 print('GEN',k,'best_cagr',round(top['result']['cagr_diagnostic']*100,2),'mdd',round(top['result']['mdd_diagnostic']*100,2),'best_fitness',round(fit['fitness'],5),'fit_cagr',round(fit['result']['cagr_diagnostic']*100,2),'fit_mdd',round(fit['result']['mdd_diagnostic']*100,2))
top=sorted(seen.values(),key=lambda x:x['result'].get('cagr_diagnostic') or -999,reverse=True)[:5]
for x in top:print('TOP_CAGR',x['chromosome_id'][:15],x['origin_niche'],round(x['result']['cagr_diagnostic']*100,2),round(x['result']['mdd_diagnostic']*100,2),x['generation'])
