"""Validate merged coverage, preserve all discovery references, and write review report."""
import json,hashlib,sqlite3
from pathlib import Path
P=Path(__file__).resolve().parent;A=P.parent/'ga8_forward_all_20261029'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(P/'merged_summary.json');m=read(P/'manifest.json');rows=[json.loads(x) for x in (P/'merged_results.jsonl').read_text().splitlines()];q=read(A/'qualifiers.json')
assert s['phase1_eligible']==s['phase1_tested']==5851
assert {r['behavior_sha256'] for r in rows}=={r['behavior_sha256'] for r in q}
assert len(rows)==5851 and s['cross_cohort_duplicates']==3
assert sum('phase0_forward_survivor' in r['cohort_memberships'] for r in rows)==3
assert all('phase1_training_qualifier' in r['cohort_memberships'] for r in rows)
assert sha(A/'results.jsonl')==s['source_result_sha256']
assert sha(A/'summary.json')==s['source_summary_sha256']
for path,digest in m['source_hashes'].items():assert sha(Path(path))==digest
# Explicitly retain discovery origin and parents for every Phase-1 source identity.
db=sqlite3.connect(f'file:{A}/catalog_snapshot.sqlite?mode=ro',uri=True)
lineage={ident:dict(first_phase=ph,first_generation=gen,parents=json.loads(parents)) for ident,ph,gen,parents in db.execute('SELECT id,first_phase,first_generation,parent_ids_json FROM chromosomes')};db.close()
with (P/'discovery_lineage.jsonl').open('w') as f:
 for r in rows:
  sources=[dict(id=i,**lineage[i]) for i in r['source_ids']]
  f.write(json.dumps(dict(behavior_sha256=r['behavior_sha256'],cohort_memberships=r['cohort_memberships'],source_identities=sources))+'\n')
lines=['# Frozen 2024 forward comparison','',f"All {s['phase1_tested']:,} Phase-1 training qualifiers and all three verified Phase-0 survivors are included. The three survivors overlap Phase-1 behaviors: {len(rows):,} unique replays, three dual memberships, zero supplemental heavy replays.",'','Window: 2024-01-01 through 2024-12-31 (252 sessions), fresh $100,000 each. Frozen genes, manager, entry and exit rules, costs and data match the main job. No evolution, production writes, or selection using 2024 results.','', '| Phase-0 survivor ID | CAGR | Max drawdown | Calmar | Final NAV | Comparison gate |','|---|---:|---:|---:|---:|---|']
for r in s['phase0_outcomes']:
 x=r['forward'];lines.append(f"| `{r['survivor_id']}` | {x['cagr']:.2%} | {x['max_drawdown']:.2%} | {x['calmar']:.3f} | ${x['final_nav']:,.2f} | {'Pass' if r['forward_success'] else 'Fail'} |")
lines+=['','Comparison gate: CAGR > 1.5 × abs(MDD), abs(MDD) < 20%, at least 30 closed trades when available. This is an outcome label only; all candidates remain included.','','Benchmarks:']
for n,b in s['benchmarks'].items():lines.append(f"- {n}: CAGR {b['cagr']:.2%}, max drawdown {b['max_drawdown']:.2%}, final NAV ${b['final_nav']:,.2f}.")
lines+=['',f"QQQ: {s['QQQ']}",'','Evidence: `manifest.json` hashes the original 2023 forward JSONL, summary and saved checkpoint corroborating all three parents. `cohort.json` retains exact genomes, managers, discovery phase/generation, parents and 2023 evidence. `merged_results.jsonl` retains both memberships; `discovery_lineage.jsonl` preserves discovery metadata for every source identity. Main training observations and qualifier records remain in `../ga8_forward_all_20261029/`.','','Limitations:']+[f'- {x}' for x in s['limitations']]
(P/'REPORT.md').write_text('\n'.join(lines)+'\n')
(P/'verification.json').write_text(json.dumps(dict(passed=True,unique_behaviors=len(rows),phase1_memberships=5851,phase0_memberships=3,source_hashes_unchanged=True,discovery_lineage_sha256=sha(P/'discovery_lineage.jsonl')),indent=2)+'\n')
print('\n'.join(lines))
