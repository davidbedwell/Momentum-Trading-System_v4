import sqlite3,json,glob,os
p='/opt/mts/thunder-migration/mts-certification-20261011/cagr_mdd_library_20261013/STRATEGY_BANK_INDEX.sqlite';c=sqlite3.connect('file:'+p+'?mode=ro',uri=True)
for name,sql in c.execute("select name,sql from sqlite_master where type='table'"):
 print('TABLE',name,'SCHEMA',sql[:1800]);print('COUNT',c.execute('select count(*) from "'+name+'"').fetchone()[0]);print('EXAMPLE',str(c.execute('select * from "'+name+'" limit 1').fetchone())[:1200])
print('CHECKPOINTS')
for p in glob.glob('/opt/mts/thunder-migration/**/Research/**/*',recursive=True):
 if os.path.isfile(p) and any(k in os.path.basename(p).lower() for k in ['chromosome','genome','bank','manifest']):
  if any(p.endswith(x) for x in ('.json','.jsonl','.sqlite','.parquet')):print(p)
