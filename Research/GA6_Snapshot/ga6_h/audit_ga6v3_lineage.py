import sqlite3
p='/opt/mts/ga6/runs/A_v2_full_evolution_20261022/'
for f in ('structural_manifest.sqlite','structural_trials.sqlite'):
 c=sqlite3.connect('file:'+p+f+'?mode=ro',uri=True)
 print(f,[(r[0],r[1]) for r in c.execute("select name,sql from sqlite_master where type='table'")])
 c.close()
