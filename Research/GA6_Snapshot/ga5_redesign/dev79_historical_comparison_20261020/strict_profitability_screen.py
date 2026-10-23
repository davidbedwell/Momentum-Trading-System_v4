import json,csv,collections,hashlib
from pathlib import Path
root=Path('/opt/mts/ga5_redesign/dev79_historical_comparison_20261020');sources=[Path('/opt/mts/ga5_redesign/dev79_ga5_500_gen1/all_evaluations.jsonl'),Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/all_evaluations.jsonl')]
seen={};stats=collections.Counter();source_stats={}
for src in sources:
 if not src.exists():continue
 local=collections.Counter()
 with src.open() as f:
  for line in f:
   local['rows']+=1
   try:
    x=json.loads(line);r=x['result'];c=float(r['cagr_diagnostic']);m=abs(float(r['mdd_diagnostic']));t=int(r.get('shadow',{}).get('closed_trades',0));cal=c/m if m else 0
   except (KeyError,ValueError,TypeError,ZeroDivisionError):local['invalid']+=1;continue
   if not(c>0.15 and 0<m<0.20 and cal>1.5):continue
   local['threshold_pass_rows']+=1
   if t<100:local['insufficient_trades']+=1;continue
   local['trade_pass_rows']+=1
   k=x.get('chromosome_id');z={'chromosome_id':k,'generation':x.get('generation'),'niche':x.get('origin_niche'),'genome':x.get('genome'),'cagr_pct':c*100,'mdd_pct':m*100,'calmar':cal,'closed_shadow_trades':t,'fitness':x.get('fitness'),'source':str(src),'status':r.get('status')}
   if k not in seen or z['calmar']>seen[k]['calmar']:seen[k]=z
 source_stats[str(src)]=dict(local);stats.update(local)
ranked=sorted(seen.values(),key=lambda z:(z['calmar'],z['cagr_pct']),reverse=True)
with (root/'ga5_strict_threshold_qualifiers.json').open('w') as f:json.dump(ranked,f,indent=2)
with (root/'ga5_strict_threshold_qualifiers.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['rank','chromosome_id','generation','niche','cagr_pct','mdd_pct','calmar','closed_shadow_trades','source'])
 for i,z in enumerate(ranked,1):w.writerow([i]+[z[k] for k in ('chromosome_id','generation','niche','cagr_pct','mdd_pct','calmar','closed_shadow_trades','source')])
manifest={'filters':'CAGR >15%, absolute MDD <20% and >0, Calmar >1.5, shadow closed trades >=100','scope':'GA5 exploratory DEV79 only','source_stats':source_stats,'distinct_qualifying_chromosomes':len(ranked),'best':ranked[0] if ranked else None}
(root/'ga5_strict_threshold_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps({k:v for k,v in manifest.items() if k!='best'},indent=2));print('BEST',json.dumps({k:v for k,v in (ranked[0] if ranked else {}).items() if k!='genome'},indent=2))
