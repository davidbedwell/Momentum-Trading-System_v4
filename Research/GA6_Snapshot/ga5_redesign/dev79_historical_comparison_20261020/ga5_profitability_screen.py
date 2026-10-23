import json,hashlib,csv,collections
from pathlib import Path
root=Path('/opt/mts/ga5_redesign/dev79_historical_comparison_20261020');sources=[Path('/opt/mts/ga5_redesign/dev79_ga5_500_gen1/all_evaluations.jsonl'),Path('/opt/mts/ga5_redesign/dev79_niche_origin_500x1000_20261019/all_evaluations.jsonl')]
selected={};counts=collections.Counter();by_source={}
for src in sources:
 if not src.exists():continue
 n=0
 with src.open() as f:
  for line in f:
   try:x=json.loads(line);r=x.get('result',{});c=float(r.get('cagr_diagnostic',-999));m=abs(float(r.get('mdd_diagnostic',0)));t=int(r.get('shadow',{}).get('closed_trades',0));n+=1
   except (ValueError,TypeError,AttributeError):counts['malformed']+=1;continue
   if c<0.10 or m<0.03 or t<100:counts['filtered']+=1;continue
   k=x.get('chromosome_id') or hashlib.sha256(json.dumps(x.get('genome',{}),sort_keys=True).encode()).hexdigest();z={'chromosome_id':k,'generation':x.get('generation'),'niche':x.get('origin_niche'),'genome':x.get('genome'),'cagr_pct':c*100,'mdd_pct':m*100,'calmar':c/m,'closed_shadow_trades':t,'fitness':x.get('fitness'),'source':str(src),'evaluation_status':r.get('status'),'validation':'EXPLORATORY_DEV79_ONLY'}
   if k not in selected or z['calmar']>selected[k]['calmar']:selected[k]=z
   counts['qualified_rows']+=1
 by_source[str(src)]=n
ranked=sorted(selected.values(),key=lambda x:(x['calmar'],x['cagr_pct']),reverse=True);top=ranked[:100]
(root/'ga5_profitability_screen_top100.json').write_text(json.dumps(top,indent=2));
with (root/'ga5_profitability_screen_top100.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['rank','chromosome_id','generation','niche','cagr_pct','mdd_pct','calmar','closed_shadow_trades','source'])
 for i,z in enumerate(top,1):w.writerow([i]+[z[k] for k in ('chromosome_id','generation','niche','cagr_pct','mdd_pct','calmar','closed_shadow_trades','source')])
manifest={'screen':'CAGR >=10%, MDD >=3%, >=100 shadow closed trades; exploratory only','source_rows':by_source,'counts':dict(counts),'unique_qualified':len(ranked),'top100_count':len(top),'top_calmar':top[0]['calmar'] if top else None,'above2_count':sum(z['calmar']>2 for z in ranked),'generation_counts':dict(collections.Counter(str(z['generation']) for z in top)),'source_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources if p.exists()},'files_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in ('ga5_profitability_screen_top100.json','ga5_profitability_screen_top100.csv')}}
(root/'ga5_profitability_screen_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
