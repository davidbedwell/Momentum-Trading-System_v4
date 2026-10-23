import json,tempfile,sqlite3
from pathlib import Path
import pandas as pd
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
from research_niche_recognizer import label_frame
from policy_shadow_runner import run_and_persist
root=Path('/opt/mts');cp=json.loads((root/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text());cs=[StructuralCandidate.restore(z) for z in cp['members']]
f=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet');g=f[f.ticker=='ACN'].sort_values('date');g=g[(g.date>='2023-01-01')&(g.date<'2024-05-01')]
n={str(r.date)[:10]:r.research_niche for r in label_frame(g).itertuples(index=False)}
rows=g.to_dict('records');dates={str(r['date'])[:10] for r in rows}
policy=json.loads((root/'ga5_redesign/exploratory79_policy.json').read_text())
member={(d,t):v for d,t,v in policy['membership'] if t=='ACN' and d in dates}
veto={d:policy['risk_veto'][d] for d in dates}
blocked={t:frozenset(v) for t,v in policy['blocked'].items()}
with tempfile.TemporaryDirectory() as tmp:
 result=run_and_persist(rows,cs,n,membership=member,blocked=blocked,risk_veto=veto,db_path=str(Path(tmp)/'shadow.sqlite'),cohort='DEV79')
 db=sqlite3.connect(Path(tmp)/'shadow.sqlite');nd=db.execute('select count(*) from decisions').fetchone()[0];no=db.execute('select count(*) from outcomes').fetchone()[0]
 assert nd==len(result['decisions']) and no==len(result['trades']),(nd,no,len(result['trades']))
 assert no>0 and all(1<=t['holding_sessions']<=40 for t in result['trades'])
 assert db.execute('select count(*) from outcomes o join decisions d using(decision_id) where o.outcome_asof<=d.asof').fetchone()[0]==0
 print('PASS policy-gated replay + delayed learning outcomes',nd,'decisions',no,'matured trades')
