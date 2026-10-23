import sqlite3,json,csv,hashlib,os
from pathlib import Path
base=Path('/opt/mts/ga5_redesign/dev79_historical_comparison_20261020');db='/opt/mts/thunder-migration/mts-certification-20261011/cagr_mdd_library_20261013/STRATEGY_BANK_INDEX.sqlite';c=sqlite3.connect('file:'+db+'?mode=ro',uri=True)
summary={'source':db,'counts':{},'studies':[],'definition_status':[]}
summary['counts']['strategies']=c.execute('select count(*) from strategies').fetchone()[0]
summary['counts']['measurements']=c.execute('select count(*) from measurements').fetchone()[0]
summary['counts']['nonempty_definitions']=c.execute("select count(*) from strategies where definition is not null and length(trim(definition))>2").fetchone()[0]
summary['studies']=c.execute('select study,count(*) from strategies group by study order by count(*) desc').fetchall()
summary['definition_status']=c.execute('select definition_status,count(*) from strategies group by definition_status').fetchall()
with (base/'complete_chromosome_definitions.jsonl').open('w') as f:
 for key,h,study,ch,hor,definition,status in c.execute('select strategy_key,definition_hash,study,chromosome,horizon,definition,definition_status from strategies'):
  f.write(json.dumps({'strategy_key':key,'definition_hash':h,'study':study,'chromosome':ch,'horizon':hor,'definition':json.loads(definition) if definition else None,'definition_status':status},separators=(',',':'))+'\n')
with (base/'chromosome_performance_index.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['strategy_key','study','chromosome','horizon','definition_hash','definition_status','cohort','cagr','mdd','calmar','measurement_status','source'])
 for row in c.execute('select s.strategy_key,s.study,s.chromosome,s.horizon,s.definition_hash,s.definition_status,m.cohort,m.cagr,m.mdd,m.calmar,m.status,m.source from strategies s left join measurements m on s.strategy_key=m.strategy_key'):w.writerow(row)
for fn in ('complete_chromosome_definitions.jsonl','chromosome_performance_index.csv'):
 p=base/fn;h=hashlib.sha256();
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 summary[fn]={'bytes':p.stat().st_size,'sha256':h.hexdigest()}
(base/'chromosome_recovery_manifest.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2),flush=True)
