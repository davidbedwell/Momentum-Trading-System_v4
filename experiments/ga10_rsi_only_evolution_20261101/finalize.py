"""Summarize frozen search and audits; does not modify or select genomes."""
import json,hashlib
from pathlib import Path
import pandas as pd
import numpy as np
P=Path(__file__).resolve().parent
s=json.loads((P/'terminal.json').read_text());m=pd.read_csv(P/'metrics.csv');f=pd.read_csv(P/'frontier.csv');c=pd.read_csv(P/'candidates.csv');v=json.loads((P/'verification.json').read_text())
assert all(v.values())
# Cumulative training champions, with genome, retained for every completed generation.
history=[];best=None
for gen,group in c.groupby('generation',sort=True):
 feasible=group[group.mdd<.25]
 if len(feasible):
  row=feasible.loc[feasible.cagr.idxmax()]
  if best is None or row.cagr>best.cagr:best=row
 if best is not None:history.append(dict(completed_generation=int(gen),champion_origin_generation=int(best.generation),candidate=int(best.candidate),cagr=best.cagr,mdd=best.mdd,calmar=best.calmar,genome=best.genome))
pd.DataFrame(history).to_csv(P/'champion_history.csv',index=False)
lines=['','Terminal audit and runtime:','',f"Completed {s['completed']} generations ({len(c):,} candidate evaluations); search runtime {s['elapsed']:.2f} seconds, full invocation including compilation, smoke and frozen evaluation {s['total_invocation_seconds']:.2f} seconds. Stop reason: {s['status']}. Terminal stagnation count: {s['stale']}. Checkpoint includes next population, RNG state, exact frontier and meaningful-improvement archive.",'',f"Final training frontier: {len(f)} points, {int((f.mdd<.25).sum())} feasible and {int((f.mdd>=.25).sum())} infeasible. All {len(c[c.mdd>=.25]):,} infeasible candidate results remain in candidates.csv. Best infeasible CAGR result:",'']
inf=c[c.mdd>=.25]
if len(inf):
 z=inf.loc[inf.cagr.idxmax()];lines.append(f"Generation {int(z.generation)}, candidate {int(z.candidate)}: CAGR {z.cagr:.2%}, daily MDD {z.mdd:.2%}, Calmar {z.calmar:.3f}.")
else:lines.append('No infeasible candidates occurred.')
lines+=['','Training Pareto extremes:','','|Extreme|CAGR|Daily MDD|Calmar|','|---|---:|---:|---:|']
for label,z in [('Maximum CAGR',f.loc[f.cagr.idxmax()]),('Minimum MDD',f.loc[f.mdd.idxmin()]),('Maximum Calmar',f.loc[f.calmar.idxmax()])]:lines.append(f'|{label}|{z.cagr:.2%}|{z.mdd:.2%}|{z.calmar:.3f}|')
lines+=['','The entire exact training Pareto set is in [frontier.csv](frontier.csv); every frozen point is evaluated in the `dev79_*_frozen_frontier.csv` and `dev87_*_frozen_frontier.csv` files without reselection. Training champion history including genomes is in [champion_history.csv](champion_history.csv).','', 'Frozen feasible-CAGR champion versus benchmarks:']
for split,grp in m.groupby('split',sort=False):
 z=grp[grp.policy=='feasible_cagr'].iloc[0];b=grp[grp.policy=='monthly_rsi_buy_hold'].iloc[0]
 lines+=['',f"{split}: CAGR difference versus monthly RSI buy/hold {z.cagr-b.cagr:+.2%}; daily MDD difference {z.mdd-b.mdd:+.2%}. Risk preference {'met' if z.mdd<.25 else 'NOT met'}. Cash benchmark CAGR/MDD/Calmar 0/0/0 (Calmar defined as zero for the flat path)."]
lines+=['','Interpretation: the selected training champion did not generalize. DEV79 evaluation CAGR was 1.35% versus 11.82% for monthly RSI buy/hold; DEV87 evaluation CAGR was -0.83% versus 20.14%. The evolved strategy met the drawdown preference in these evaluations but sacrificed return. No evaluation-based retuning or replacement occurred.','', 'Calmar pathology: the maximum-Calmar training genome earned only 0.0159% annual CAGR with approximately 0.000000000631% daily MDD, producing a ratio around 25 million. This near-cash denominator artifact is retained transparently in the frontier and champion table; it is not evidence of a useful high-return strategy. Zero or extremely tiny MDD makes Calmar unstable.','', 'The selected CAGR champion executed all action branches in training: 13 entries, 748 adds, 196 reductions, 12 exits and 3186 held-position days. Evaluation also includes executed reductions. The forced crash test independently proved stop liquidation followed by cash re-entry; re-entry remains an evolved choice, not a promised recovery.']
lines+=['','Accounting and integrity audit passed: independent baseline NAV parity, eligible entries with missing optional predictors, contiguous completed-generation counts, exact stagnation counter reconstruction, all final frontier genomes replayed, nondominance, maximum feasible training CAGR champion, all new entries screened, exposure bounds and source hash. See [verification.json](verification.json).','', 'A preliminary search was stopped before evaluation when an inherited optional-feature finite gate was found. That gate was removed; the study restarted from the original seed. Discarded artifacts and explanation are preserved under `aborted_finite_feature_gate/` and did not seed this search.','', 'Checkpoint resume was separately tested in a temporary copy: saved RNG and next population were preserved and an uncommitted extra generation-log row was trimmed. See resume_verification.json.','', 'No production files were changed. Reproduce or resume with `bash experiments/ga10_rsi_only_evolution_20261101/run.sh`; after completion run `verify.py` and `finalize.py` with `/opt/mts/.venv/bin/python`. An exception stops the study and creates ERROR_AUDIT.txt; no exception triggers an automatic continuation.']
report=P/'REPORT.md'
base=report.read_text().split('\nTerminal audit and runtime:')[0].rstrip()
report.write_text(base+'\n'+'\n'.join(lines)+'\n')
sources=[P/'study.py',P/'prototype.py',P/'test_study.py',P/'verify.py',P/'finalize.py',P/'champions.json',P/'freeze.json',P/'checkpoint.json',Path('/opt/mts/portfolio_evolution_dev80/dev80_raw_no_smci.parquet'),P.parent/'dev87_rsi_frozen_validation_20261101/dev87_raw.parquet']
(P/'artifact_hashes.json').write_text(json.dumps({str(x):hashlib.sha256(x.read_bytes()).hexdigest() for x in sources},indent=2))
print('\n'.join(lines[:12]))
