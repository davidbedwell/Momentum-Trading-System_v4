import json,sqlite3,statistics
from pathlib import Path
p=Path('/opt/mts/ga6/runs')
base=json.loads((p/'A_v2_matched_control_20261022/baseline_results.json').read_text())
db=sqlite3.connect(str(p/'A_v2_end_to_end_20261022/structural_manifest.sqlite'))
rdb=sqlite3.connect(str(p/'A_v2_end_to_end_20261022/structural_evaluations.sqlite'))
print('candidate count',db.execute('select count(*) from candidates').fetchone()[0])
print('occurrence',db.execute('select * from occurrences limit 1').fetchone())
print('candidate sample',json.loads(db.execute('select definition_json from candidates limit 1').fetchone()[0]).keys())
print('result count',rdb.execute('select count(*) from evaluations').fetchone()[0])
