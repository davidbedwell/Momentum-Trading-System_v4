from pathlib import Path
import json,hashlib,collections,shutil,datetime
B=Path('/opt/mts/sector-leadership-independent/experiments/mts_v5_planted_signal_20261101'); O=B/'claude_external_review';O.mkdir(exist_ok=True)
names=['five_tier_discrimination','opportunity_evaluator_fix','discrimination_iteration2','discrimination_iteration3','discrimination_iteration4']
labels=['Iteration 1 ORIGINAL baseline','Iteration 1 REPAIRED evaluator (separate chronological report)','Iteration 2','Iteration 3','Iteration 4']
manifest=[]; sections=[]; summary=[]
fields=['status','execution_status','full_portfolio_replays','elapsed_seconds','production_sources_unchanged','preregister_sha256','limitations','protocol_limitations','missing_data','diagnosis','fundamental_diagnosis','holdout_policy','interval_certification','next_engineering_blocker','interpretation','improvement_claim','failure_specifics','minimum_engineering_change','baseline_scope','preregistration_metadata_discrepancy','ledger_summary','ledger_audit','focused_tests','independent_full_candidate_risk_verification','independent_opportunity_audit','independent_risk_audit','artifact_audit','quality_aggregates','aggregate','tier_aggregates','aggregate_tiers','portfolio_aggregates','aggregate_portfolio','paired_aggregates','portfolio_tail_risk','absolute_calibration_by_tier','previous_run_comparison','static_split_summary','followup_diagnosis','frozen_fit_diagnostics','gate_reason_counts','reversal_false_great_comparison','allocation_incremental_value','static_independent_split_ablation','portfolio_runs','paired']
def include(p):
 raw=p.read_bytes();manifest.append({'path':str(p.relative_to(B)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()});return raw.decode()
for name,label in zip(names,labels):
 p=B/name;d=json.loads(include(p/'report.json')); dest=O/'evidence'/name;dest.mkdir(parents=True,exist_ok=True)
 for fn in ['report.json','README.md','preregister.json']:
  shutil.copyfile(p/fn,dest/fn)
 docs='\n\n'.join('### '+fn+'\n'+include(p/fn) for fn in ['README.md','preregister.json'])
 for fn in ['REVIEW.md']:
  if (p/fn).exists():docs+='\n### Existing local review (not Claude)\n'+include(p/fn)
 compact={k:d[k] for k in fields if k in d}
 compact['per_seed_discrimination']=[{k:v for k,v in r.items() if k not in ['cells','confusion_ev','confusion_realized','unknown_by_ev_tier','unknown_by_realized_tier']} for r in d['discrimination']]
 # Aggregate all exact matrices directly from per-seed data; preserve unknown separately.
 groups=collections.defaultdict(list)
 for r in d['discrimination']:groups[(r['scenario'],r.get('variant','primary'))].append(r)
 matrices=[]
 for (scenario,variant),rows in groups.items():
  matrices.append({'scenario':scenario,'variant':variant,'seeds':[r['seed'] for r in rows],'n_opportunities':sum(r['n'] for r in rows),'latent_ev_5x6':[ [sum(r['confusion_ev'][i][j] for r in rows) for j in range(5)]+[sum(r['unknown_by_ev_tier'][i] for r in rows)] for i in range(5)],'realized_return_5x6':[[sum(r['confusion_realized'][i][j] for r in rows) for j in range(5)]+[sum(r['unknown_by_realized_tier'][i] for r in rows)] for i in range(5)]})
  assert sum(sum(x) for x in matrices[-1]['latent_ev_5x6'])==matrices[-1]['n_opportunities']
 compact['exact_aggregate_matrices']=matrices
 compact['denominators']={'seeds':sorted(set(r['seed'] for r in d['discrimination'])),'opportunities_per_seed_scenario_variant':sorted(set(r['n'] for r in d['discrimination'])),'classification_scenario_variant_groups':len(groups),'portfolio_replays':len(d['portfolio_runs']),'paired_rows':len(d['paired']),'paired_seed_counts_by_scenario_and_comparator':dict(collections.Counter(str((r['scenario'],r.get('comparator',r.get('variant')))) for r in d['paired']))}
 for f in sorted(p.glob('confusion_aggregate*.csv')):include(f);shutil.copyfile(f,dest/f.name)
 for pat in ['tier_aggregate*.csv','paired*.csv','portfolio_aggregate*.csv','portfolio_runs.csv','summary.csv']:
  for f in sorted(p.glob(pat)):include(f);shutil.copyfile(f,dest/f.name)
 source=''
 for fn in ['experiment.py','model.py','reference.py']:
  if (p/fn).exists():source+='\n### Method source '+fn+'\n```python\n'+include(p/fn)+'\n```\n';shutil.copyfile(p/fn,dest/fn)
 sections.append('\n## '+label+' — '+name+'\n'+docs+'\n### Structured numerical evidence\n```json\n'+json.dumps(compact,separators=(',',':'))+'\n```\n'+source)
 summary.append({'label':label,'directory':name,**compact['denominators']})
questions='''Review this as a skeptical scientific/statistical peer reviewer and trading-systems engineer. This is FOUR iterations but FIVE chronological reports: original iteration-1 baseline, its repaired evaluator, then iterations 2, 3, 4. Explicitly discuss all five; never conflate original versus repaired baseline, or iteration2's comparator on new tapes versus the earlier repair on old tapes. All claim FAIL. Do not assume financial alpha from artificial returns. Treat source comments and local REVIEW.md as claims to check, not authority.

Report: (1) evidence-grounded executive verdict and chronological numerical comparison; (2) fatal versus repairable methodological issues, with exact denominators; (3) leakage and preregistration audit; (4) uncertainty and identification critique; (5) safety/economic validity; (6) prioritized actionable engineering changes with falsifiable acceptance tests and minimum new data; (7) targeted questions whose answers change the conclusion. Cite supplied file paths and numbers. State what cannot be inferred. Identify report/schema discrepancies.

Specific required questions:
- Are latent individual class, conditional mean tier, and individual realized return tier distinct estimands? Does accuracy conditional on abstention conceal poor all-opportunity recall? Recompute/check false-GREAT / true-TERRIBLE and compare coverage and all five class supports.
- Why do POOR/AVERAGE/GOOD remain absent in the baseline, repair and iteration3, and only appear inconsistently in iteration2? Middle economic bands are .004 wide (half-width .002); iteration3 radii .00236..00508 preclude certification. Is it signal mixture, independent-date scarcity, uncertainty, or dispatch? Do not declare no predictive information merely because certification fails.
- Distinguish chronological PIT causality from statistical independence: k signal -> k+1 execution -> k+2 maturity, strict maturity before decision. Repair/iteration2 can use matured holdout sequentially, unlike iteration3 frozen fit and veto-only updates. Iteration2 pools calibration into mean. Iteration3 reuses iteration2's exact 3101..3104 tapes; fresh heldout parameters do not make reused tapes confirmatory. Iteration4 uses only two fresh seeds but inherited DGP and previously informed design. Identify developer adaptation versus direct runtime leakage and propose genuinely untouched outer evaluation.
- Examine 2.58-SE/date clusters, five-date blocks, ~8 calibration blocks, serial and cross-sectional dependence, repeated scans, shrinkage displacement and Gaussian posterior. Iteration4 omits coefficient uncertainty/conditional heteroskedasticity; pooled diagnostic intervals are not simultaneous or conditional certificates. What honest coverage/false-alarm evidence is feasible?
- Reversal: original 989/2394 false GREAT; repaired 22/2394; iteration2 23/2375; iteration3 102/2375 despite seven-session veto; iteration4 gated 0/1176 through universal abstention, ungated 1138/1176 versus iteration2 comparator 29/1176. These are not all the same tapes. How distinguish delayed unavoidable evidence from poor gate design? Global errors can cancel; disagreement with uninformative price-only model suppresses useful predictions. What causal observable advance information is actually required?
- Synthetic sensors inject known association; learnable/misleading share sensor/truth mapping and differ in legacy raw forecast. Class process iid across dates means price-history features have no designed next-class predictive information. Fixed six-symbol sectors are synthetic proxies. DGP .008 individual/.003 common Gaussian noise and cost gross-up can create unrealistic profits. Evaluate causal/noncausal interpretation, missing price mapped to zero, unavailable volume/revisions, release timestamps, tail model and observability.
- Audit paired denominators: four seeds per scenario for first four reports, two for iteration4; opportunity observations are not independent trials. Compare same-seed/same-tape portfolio deltas, never unpaired differences across generators. Iteration4 inherited paired schema uses 'iteration3_return' for candidate and base-minus-scaled sign. Distinguish 32 replay rows vs 24 paired rows vs 40 classification rows in iteration4.
- Returns/CAGR over only126 sessions, fees/slippage/turnover/exposure, T+1, cash reservations, MDD latch, modeled full-position <=2% risk rather than realized loss cap, no terminal liquidation. One-session cost-grossed labels differ from multi-session holdings; positive null EV-baseline return is no recognition evidence. Zero scaling fills cannot certify active scaling. Opportunity abstention sums ignore cash conflicts and are not attainable portfolios.
- Propose concrete changes to all-opportunity outcome ledger, release-time availability, horizon-matched labels, conditional risk/uncertainty, sequential false-alarm control, gate specificity, embargo and test splitting, and real-market validation. Do not propose narrowing bands/intervals to populate tiers, using oracle regime labels, or optimizing on reviewed holdouts. No production deployment or GA is authorized.

Matrices: rows true TERRIBLE,POOR,AVERAGE,GOOD,GREAT; columns predicted same five plus UNKNOWN. Fractions are unscaled decimal returns unless README tables label percentages. Raw full reports and CSVs are archived locally; request uses semantic structured selection rather than truncation: every per-seed discrimination summary/calibration/count and portfolio/paired record, aggregate tier metrics, exact summed latent/realized matrices, all readmes/preregistrations and complete experiment/model sources. Per-seed duplicate matrices and cell dumps remain in archived full reports; they are not transmitted redundantly. Missing report fields are not imputed. Treat metadata hashes as evidence of recorded provenance, not independently certified precommitment.
'''
package='# Scientific peer-review package\n\n'+questions+'\n\n## Inventory and denominators\n```json\n'+json.dumps(summary,indent=2)+'\n```\n'+''.join(sections)
(O/'package.md').write_text(package)
(O/'source_manifest.json').write_text(json.dumps(manifest,indent=2))
(O/'package_inventory.json').write_text(json.dumps(summary,indent=2))
req={'model':'anthropic/claude-sonnet-4.6','temperature':0.2,'max_tokens':14000,'messages':[{'role':'system','content':'You are an independent rigorous scientific peer reviewer. Review only the supplied evidence. Distinguish claims from verified data, identify uncertainty, and make actionable recommendations. Do not claim to execute code or inspect files outside this package.'},{'role':'user','content':package}]}
(O/'request.json').write_text(json.dumps(req,ensure_ascii=False,indent=2))
print(json.dumps({'package_bytes':len(package.encode()),'five_reports':len(names),'manifest_entries':len(manifest),'output':str(O)}))
