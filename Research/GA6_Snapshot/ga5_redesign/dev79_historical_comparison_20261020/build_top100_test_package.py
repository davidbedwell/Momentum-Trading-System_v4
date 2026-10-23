import sqlite3,json,csv,re,collections,hashlib
from pathlib import Path
import pyarrow.parquet as pq
root=Path('/opt/mts/ga5_redesign/dev79_historical_comparison_20261020');db='/opt/mts/thunder-migration/mts-certification-20261011/cagr_mdd_library_20261013/STRATEGY_BANK_INDEX.sqlite';con=sqlite3.connect('file:'+db+'?mode=ro',uri=True)
# Normalize positive MDD magnitudes; restrict to measurable DEV80 cohorts and unique chromosomes.
rows=con.execute("select s.strategy_key,s.study,s.chromosome,s.horizon,s.definition_hash,s.definition,s.definition_status,m.cohort,m.cagr,m.mdd,m.calmar,m.status,m.source from strategies s join measurements m on s.strategy_key=m.strategy_key where m.cagr between 0 and 150 and abs(m.mdd) between 3 and 90 and m.cohort in ('DEV80','DEV87','DEV50')").fetchall()
print('ELIGIBLE_ROWS',len(rows),flush=True)
bykey={}
for z in rows:
 key=z[0];c=z[8];dd=abs(z[9]);score=c/dd
 if key not in bykey or score>bykey[key][0]:bykey[key]=(score,z)
ranked=sorted(bykey.values(),key=lambda a:(a[0],a[1][8]),reverse=True)
# Balance growth and Calmar frontiers; unique definitions; selection is research screening, not validation.
byc=sorted(bykey.values(),key=lambda a:(a[1][8],a[0]),reverse=True);chosen=[];seen=set()
for pool in (ranked[:70],byc[:70],ranked,byc):
 for score,z in pool:
  if z[4] in seen:continue
  chosen.append((score,z));seen.add(z[4])
  if len(chosen)==100:break
 if len(chosen)==100:break
cols=set(pq.read_schema('/opt/mts/ga5_redesign/exploratory79_ga4_enriched.parquet').names)
records=[];missing=collections.Counter();families=collections.Counter()
for rank,(score,z) in enumerate(chosen,1):
 key,study,ch,hor,h,definition,status,cohort,cagr,mdd,calmar,ms,source=z;genes=json.loads(definition);features=set()
 def walk(x):
  if isinstance(x,dict):
   for k,v in x.items():
    if isinstance(v,str) and ('feature' in k or k in ('breadth','security_context','price_feature')):features.add(v)
    walk(v)
  elif isinstance(x,list):
   for y in x:walk(y)
 walk(genes)
 for gene in genes:
  if isinstance(gene,list) and gene:families[str(gene[0])]+=1
 coverage={f:('DIRECT' if f in cols else 'GA4_TANH_ONLY' if 'ga4_'+f in cols else 'MISSING') for f in sorted(features)}
 for f,v in coverage.items():
  if v!='DIRECT':missing[f]+=1
 records.append({'rank':rank,'strategy_key':key,'study':study,'chromosome_id':ch,'horizon_sessions':hor,'definition_hash':h,'definition_status':status,'selected_cohort':cohort,'cagr_reported_pct':cagr,'mdd_reported_pct':mdd,'calmar_reported':calmar,'source':source,'chromosome_definition':genes,'required_features':coverage,'ready_for_exact_replay':all(v=='DIRECT' for v in coverage.values()) and False,'execution_contract_status':'NOT_VERIFIED','notes':'Portfolio accounting, signal threshold calibration, original order/fill/exit contract not yet independently recovered'})
(root/'top100_complete_chromosome_test_package.json').write_text(json.dumps(records,indent=2))
with (root/'top100_rankings.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['rank','study','chromosome','horizon','cohort','cagr_pct','mdd_pct','calmar','definition_hash','features_unavailable_or_transformed','execution_verified'])
 for z in records:w.writerow([z['rank'],z['study'],z['chromosome_id'],z['horizon_sessions'],z['selected_cohort'],z['cagr_reported_pct'],z['mdd_reported_pct'],z['calmar_reported'],z['definition_hash'],sum(x!='DIRECT' for x in z['required_features'].values()),False])
manifest={'eligible_measurements':len(rows),'unique_strategies':len(bykey),'selected':len(records),'selection':'70 highest Calmar then 30 highest CAGR, deduped by definition hash; research only','study_counts':dict(collections.Counter(z['study'] for z in records)),'cohort_counts':dict(collections.Counter(z['selected_cohort'] for z in records)),'feature_gaps':missing.most_common(30),'gene_families':dict(families),'exact_replay_ready':sum(z['ready_for_exact_replay'] for z in records),'replay_blocker':'Original signal/threshold calibration and execution semantics not verified; GA4 features are tanh transformed in DEV79 file','files':{}}
for name in ('top100_complete_chromosome_test_package.json','top100_rankings.csv'):
 p=root/name;manifest['files'][name]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(root/'top100_manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2),flush=True)
