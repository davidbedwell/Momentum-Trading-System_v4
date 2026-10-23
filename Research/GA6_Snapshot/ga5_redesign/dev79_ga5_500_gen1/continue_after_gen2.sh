#!/bin/bash
set -euo pipefail
cd /opt/mts
OUT=ga5_redesign/dev79_ga5_500_gen1
while pgrep -f '^.venv/bin/python -u ga5_redesign/runner_unified.py .*--generations 2 ' >/dev/null; do sleep 15; done
.venv/bin/python - <<'PY'
import json,sys
p='ga5_redesign/dev79_ga5_500_gen1/checkpoint_unified.json'
s=json.load(open(p));assert s['generation']==2, f"Generation 2 not completed: {s['generation']}";assert len(s['members'])==500 and len(s['history'])==2
print('GEN2_CHECKPOINT_PASS',s['generation'],flush=True)
PY
.venv/bin/python - <<'PY'
import json,hashlib,sys
from pathlib import Path
sys.path.insert(0,'ga5_redesign')
from runner_v4 import engine_fingerprint
from canonical_engine import digest_file
p=Path('ga5_redesign/runner_unified.py');out=p.parent/'dev79_ga5_500_gen1';cp=out/'checkpoint_unified.json';s=json.loads(cp.read_text());assert s['generation']==2
paths=[p,p.with_name('unified_evolution.py'),p.with_name('evolution_controls.py'),p.with_name('optimizer_v3.py'),p.with_name('niche_seeds.py'),p.with_name('exit_objectives.py'),p.with_name('guarded_evaluator.py'),p.with_name('shadow_signals.py'),p.parent.parent/'ga5_chromosome_contract.py',p.with_name('dev79_niche_ga_v1')/'labels.parquet']
code=hashlib.sha256((engine_fingerprint()+''.join(digest_file(x) for x in paths)+'unrestricted').encode()).hexdigest()
backup=out/'checkpoint_unified.pre_unlimited.json';backup.write_text(cp.read_text());old=s['code'];s['code']=code;cp.write_text(json.dumps(s));(out/'unlimited_migration_audit.json').write_text(json.dumps({'old':old,'new':code,'checkpoint_generation':2,'stop':'100-generation stagnation; no finite cap','backup':str(backup)},indent=2));print('UNLIMITED_CHECKPOINT_MIGRATION_PASS',flush=True)
PY
exec .venv/bin/python -u ga5_redesign/runner_unified.py --features ga5_redesign/exploratory79_ga4_enriched.parquet --policy-file ga5_redesign/exploratory79_policy.json --output ga5_redesign/dev79_ga5_500_gen1 --generations 0 --stagnation 100 --population 500 --workers 8 --entry-mode unrestricted --diagnostic-only
