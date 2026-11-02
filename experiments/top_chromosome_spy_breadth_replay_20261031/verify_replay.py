"""Independent deterministic rerun of one latest-fold candidate per GA family."""
import sys,importlib.util,json,gzip,time
from pathlib import Path
import pandas as pd
sys.dont_write_bytecode=True
R=Path(__file__).resolve().parent
p=Path('/opt/mts/ga7-deploy/ga7_audit_v2/reports/ga7_final_518/ga6_ga7_common_v1_full_cohort_2009_2018.py')
s=importlib.util.spec_from_file_location('archived_replay',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
start=time.monotonic();m.load();rows=[]
selected=pd.read_csv(R/'selection.csv');selected=selected[selected.fold=='F3'].sort_values('score',ascending=False).groupby('system').head(1)
for z in selected.itertuples():
 summary,payload=m.replay((z.system,z.chromosome_id));assert payload is not None,summary
 old=json.load(gzip.open(z.path,'rt'));assert payload['trades']==old['trades'];assert payload['fills']==old['fills'];assert payload['nav']==old['nav']
 rows.append(dict(system=z.system,chromosome_id=z.chromosome_id,trades=len(payload['trades']),fills=len(payload['fills']),nav_sessions=len(payload['nav']),exact_equal=True))
 pd.DataFrame(rows).to_csv(R/'replay_verification.csv',index=False)
print(json.dumps(dict(elapsed_seconds=time.monotonic()-start,rows=rows)),flush=True)
