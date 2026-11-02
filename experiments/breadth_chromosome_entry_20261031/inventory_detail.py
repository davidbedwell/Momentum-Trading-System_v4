"""Retry SQLite inventories on disposable copies; never create sidecars in GA trees."""
import tempfile,shutil,sqlite3,json
from pathlib import Path
import pandas as pd
from study import ROOT

def main():
 files=pd.read_csv(ROOT/'file_inventory.csv');tables=pd.read_csv(ROOT/'sqlite_inventory.csv');rows=[]
 for p in files.loc[files.kind.eq('.sqlite'),'path']:
  if p in set(tables.path):continue
  with tempfile.TemporaryDirectory(prefix='breadth_sqlite_') as tmp:
   dest=Path(tmp)/'snapshot.sqlite';shutil.copyfile(p,dest)
   if Path(p+'-wal').exists():shutil.copyfile(p+'-wal',str(dest)+'-wal')
   con=sqlite3.connect(str(dest))
   try:
    for t, in con.execute("select name from sqlite_master where type='table'"):
     safe='"'+t.replace('"','""')+'"';cols=con.execute('pragma table_info('+safe+')').fetchall()
     rows.append(dict(path=p,table=t,rows=con.execute('select count(*) from '+safe).fetchone()[0],columns=json.dumps([c[1] for c in cols])))
   except Exception as e:rows.append(dict(path=p,error=str(e)))
   finally:con.close()
 pd.DataFrame(rows).to_csv(ROOT/'sqlite_copy_inventory.csv',index=False)
 print(pd.DataFrame(rows).to_string(index=False))
if __name__=='__main__':main()
