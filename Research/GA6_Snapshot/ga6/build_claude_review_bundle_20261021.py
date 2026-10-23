from pathlib import Path
import zipfile,json,hashlib,datetime
root=Path('/opt/mts')
base=root/'ga6'
out=base/'runs'/'GA6_INDEPENDENT_CLAUDE_REVIEW_20261021.zip'
files=['ga6/runs/ga6_production_200_v1/all_evaluations.jsonl','ga6/runs/controlled_capacity_replay_20261021.jsonl','ga6/fitness.py','ga6/fitness_policy.py','ga6/guarded_evaluator_ga6.py','ga6/evaluator_adapter.py','ga6/production_runner.py','ga6/selection.py','ga6/breeder.py','ga6/portfolio_counterfactuals.py','ga6/prospective_policy.py','ga6/prospective_replay.py','ga6/policy_evolution_oos.py','ga6/policy_research.py','ga6/GA6_RESEARCH_CONTRACT.md','ga6/exits_sizing_risk_audit_20261021.py','ga6/offline_fitness_sensitivity_20261021.py','ga6/controlled_capacity_replay_20261021.py','ga5_chromosome_contract.py','ga5_redesign/optimizer_v3.py','ga5_redesign/exit_objectives.py']
brief='''INDEPENDENT ADVERSARIAL REVIEW REQUEST — GA6 MTS, 2026-10-21

Review the attached RAW all_evaluations.jsonl, chromosome genes, evaluator, fitness code, and replay outputs. Do not accept prior assistant conclusions uncritically.

Questions:
1. Is there a fundamental paradigm mismatch between maximizing independent shadow-trade EV and cash-constrained portfolio CAGR/MDD? Identify specific code-level defects or incentives.
2. Why does higher fitness coincide with worsening tail loss? Quantify by generation, niche, trade count, and position sizing.
3. Are EVs >100% plausible, or artifacts of return accounting, split adjustments, selection, or repeated opportunities? Audit the actual implementation.
4. Examine the observed 79/20/10/5 position-capacity replay: why no difference until 5, and why more executed buys at 5?
5. Propose genuinely different strategy-discovery paradigms, including time-varying portfolio construction, regime/risk overlays, factor breadth, and concentrated leadership, without assuming any one approach works.
6. Distinguish valid in-sample research from unseen transport, out-of-sample certification, and look-ahead leakage.
7. Give an ordered falsifiable experiment plan with exact acceptance criteria, minimal leakage, estimated computational cost, and a stop rule. Preserve original raw data and running GA6 unchanged.
8. Compare only verified comparable OmniFunds claims. OmniFunds anonymized raw data NOT INCLUDED in this archive; ask for it before making numerical claims.
9. Audit whether drawdown mitigation is truly portfolio-level and whether exit policy validation has enough independent episodes.
10. Investigate why best GA6 diagnostic CAGR is ~18% with ~78% MDD, despite very high shadow EV. Do not confuse trade EV with portfolio CAGR.

Observed latest gen8 capacity replay: 79,20,10 positions 18.1357% CAGR/-78.0912% MDD; 5 positions 18.1401% CAGR/-76.9853% MDD. Diagnostic, not certified.
All data exploratory DEV79. No blind-set use is authorized.
'''
manifest=[]
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 z.writestr('REVIEW_BRIEF.txt',brief)
 for rel in files:
  p=root/rel
  if not p.is_file():continue
  z.write(p,rel)
  manifest.append({'file':rel,'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 z.writestr('MANIFEST.json',json.dumps({'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':manifest},indent=2))
print(json.dumps({'archive':str(out),'bytes':out.stat().st_size,'files':len(manifest),'manifest':manifest[-3:]},indent=2))
