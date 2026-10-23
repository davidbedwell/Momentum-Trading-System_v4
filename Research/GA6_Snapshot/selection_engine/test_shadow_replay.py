from shadow_replay import replay_symbol
from ga6.structural_independent_v2_20261022.structural_candidate import StructuralCandidate
import json,pandas as pd
from pathlib import Path
root=Path('/opt/mts');cp=json.loads((root/'ga6/runs/A_v2_full_evolution_20261022/structural_checkpoint.json').read_text())
cs=[StructuralCandidate.restore(z) for z in cp['members']]
f=pd.read_parquet(root/'ga5_redesign/exploratory79_ga4_enriched.parquet')
g=f[f.ticker=='ACN'].sort_values('date');g=g[(g.date>='2023-01-01')&(g.date<'2024-05-01')]
from research_niche_recognizer import label_frame
n={str(r.date)[:10]:r.research_niche for r in label_frame(g).itertuples(index=False)}
r=replay_symbol(g.to_dict('records'),cs,n)
assert len(r['decisions'])>0
assert all(1<=t['holding_sessions']<=40 for t in r['trades'])
assert all(t['entry_date']<t['exit_date'] for t in r['trades'])
print('PASS: historical independent shadow next-open entries/exits and 40-session cap',len(r['decisions']),'decisions',len(r['trades']),'closed trades',r['open_positions'],'open')
