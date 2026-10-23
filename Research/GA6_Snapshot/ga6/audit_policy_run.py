import json
from pathlib import Path
p=Path('/opt/mts/ga6/runs/policy_oos_smoke_v6/all_evaluations.jsonl')
rows=[json.loads(line) for line in p.open()]
print('evaluations',len(rows))
print('policy_oos_keys',sum('ga6_policy_oos' in r['result'] for r in rows))
print('eligible_oos',sum(r['result'].get('ga6_policy_oos',{}).get('eligible',False) for r in rows))
print('baseline_keys',sum('ga6_prospective_baseline' in r['result'] for r in rows))
print('oos_sample',rows[0]['result'].get('ga6_policy_oos'))
