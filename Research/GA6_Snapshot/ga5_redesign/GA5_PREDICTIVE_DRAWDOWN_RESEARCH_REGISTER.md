# GA5 DRAWNDOWN / PREDICTIVE TRADE MANAGEMENT — MASTER RESEARCH REGISTER
Created 2026-10-20. Status: planned; production optimizer remains paused. This register is the authoritative scope checklist, not evidence of completed studies.

## Primary goal
Improve actual net portfolio CAGR-versus-MDD frontier while preserving profitable opportunity, avoiding destructive drawdowns, and quantifying cash released by exits. Compare every managed policy to the unchanged entry chromosome.

## P0 — Fitness and selection audit [OPEN; BLOCKER]
- Trace runner_unified.py, optimizer_v3.py, fitness modules, pareto breeding, evaluator and promotion gates.
- Determine whether fitness uses shadow diagnostics or capital-constrained net portfolio CAGR/MDD.
- Audit objective dominance, tie-breaking, normalization, selection pressure, duplicated equivalent chromosomes and early elimination.
- Reconstruct the frontier from frozen checkpoints. Deliver reproducible baseline and discrepancy report.
- Exit criterion: exact provenance of every selection metric and agreement with replayed portfolio metrics.

## P1 — Counterfactual evaluator correctness [OPEN; BLOCKER]
- Freeze baseline chromosome/market universe, time-t features and cash ledger.
- Replay unchanged policies exactly, then hold/reduce/exit/re-enter with next-open execution, fees, slippage, cash and competing signals.
- Verify no lookahead, earnings embargo, corporate actions and calendar alignment.
- Exit criterion: baseline parity and accounting invariants verified with tests.

## P2 — Three-outcome trajectories [PILOT PARTIAL]
- A destructive loss; B recoverable drawdown; C false warning with eventual profitable continuation.
- Label future max adverse/favorable excursion, recovery time, ultimate trade outcome, time-out-of-market opportunity.
- Include all trades and suitable censoring, not only closed survivors. Report by niche, regime, horizon, winner/loser.
- Exit criterion: transparent, nonleaky multi-horizon labels with cohort distributions.

## P3 — Feature / regime discovery [PILOT PARTIAL]
- Upside/downside semivolatility, ATR, MA level/slope, price trajectory, momentum, RS, breadth, sector, market regime, trade age/peak drawdown, indicator changes and persistence.
- Search interactions, temporal patterns, and false-positive protective features.
- Exit criterion: stable incremental signal over volatility-only with walk-forward and clustered uncertainty.

## P4 — Predictive evolution [PILOT PARTIAL]
- Evolve multi-horizon probability, expected upside/downside and recovery-duration models.
- Calibrate forecasts and compare to simple baselines; penalize redundant genes and complexity.
- Train chronologically, purge overlap, group by trade/ticker/date as appropriate; no blind data.
- Exit criterion: reliable prospective risk/opportunity discrimination, not merely in-sample fit.

## P5 — Decision GA [OPEN]
- Policy choices hold, partial reduction, exit, delayed entry, re-enter; conditional sequences and cooldown.
- Multiobjective constrained fitness: net CAGR, MDD, underwater time, downside tails, upside retained, turnover.
- Compare each candidate against frozen unchanged-entry baseline. Retain Pareto diversity without promoting uneconomic policies.
- Exit criterion: measured net portfolio improvement, not shadow-trade proxy.

## P6 — Cash release economics [OPEN]
- Measure days cash is free, feasible alternative signals, redeployment capacity, foregone upside, reentry fees, cash yield.
- Compare exit-and-reenter to hold and exit-only. No hindsight opportunity selection or double counting.
- Exit criterion: auditable capital-constrained opportunity-cost ledger.

## P7 — Generalization / certification [OPEN]
- Start NICHE-0001 representative chromosomes, expand diverse exemplars to all 13 niches, then eligible bank.
- Cross-stock, chronological, niche/regime transport; multiple-comparison controls and uncertainty intervals.
- Preserve DEV79 exploratory status; DEV50 not pristine; BLIND17 untouched until frozen certification.
- Exit criterion: verified 13-niche coverage and independently supported portfolio uplift.

## Existing evidence (NOT certification)
- 26,867 eligible unique chromosomes across 13 niches cataloged by all13_niche_screen.py.
- NICHE-0001 volatility-only and directional exits generally lowered mean shadow returns.
- Volatility-only later-period adverse event ROC AUC ~0.686; five-feature model ~0.686.
- Risk-discovery GA: 120 generations / 2,746 candidates, strongest essentially high-volatility threshold; later-period adverse risk 26.7% versus 10.1% baseline. Observations overlap; chromosomes selected from full history.
- Scripts: niche0001_*; ga5_outcome_learning_pilot.py; management_ga_risk_discovery.py.
- The previous 'holdout' is not untouched independent certification.

## Execution order
P0 and P1 first (parallel audits); P2/P3 exploratory research can proceed in parallel without production mutation. Then P4 predictive evolution; P5/P6 joint policy replay; P7 expanding validation.
Every investigation must report status OPEN / RUNNING / BLOCKED / COMPLETE, artifacts, evidence, unresolved issues, and next dependency. Do not mark COMPLETE based on code creation alone.

## MANDATORY NICHE-BY-NICHE EXECUTION AMENDMENT (2026-10-20)
- Analyze each of 13 niches independently, using chromosomes designed/promoted for that specific niche. Never pool chromosomes or outcome labels across niches for the primary conclusions.
- For EACH niche, partition trajectories into (A) destructive loss/exit, (B) recoverable drawdown: hold vs exit/re-enter with days cash freed, (C) false danger signals preceding winners. Evaluate all three before declaring niche complete.
- For each niche and each category, inspect best, median, weak and diverse chromosomes; show original baseline, candidate decision policy, net CAGR, MDD, retained upside, avoided losses, cash days, turnover and reentry costs.
- First characterize niche-specific feature distributions, regime dependencies, duration-to-recovery and false positive rates; then evolve predictive models and management policies within that niche. Cross-niche transfer is a separate secondary test, never a substitute.
- Preserve chromosome lineage, time-t-only predictors, chronological validation, fixed entry baseline, and untouched blinds.
- Deliver one three-category evidence matrix per niche, one niche-specific Pareto frontier, and an all-13 comparison only after each individual niche is audited.
- Execution order: P0/P1 shared evaluator audit IN PARALLEL with A/B/C outcome profiling across ALL 13 niches. All 13 are mandatory first-wave research subjects; no niche-0001 pilot gate, no sequential niche prerequisite. Schedule resource-bounded parallel workers, preserve niche-specific chromosome lineages and separate results. Do not claim completion without all three categories and portfolio replay.

## FIRST-WAVE EXECUTION RECORD (2026-10-20)
- Completed P0 descriptive screening for ALL 13 niches: 26,867 eligible chromosomes, niche-separated. Script: /opt/mts/ga5_redesign/all13_fitness_firstwave.py. Output: dev79_niche_origin_500x1000_20261019/all13_niche_screen/all13_fitness_firstwave/all13_niche_fitness_diagnostic.csv plus top-25-by-fitness and top-25-by-Calmar CSV for each niche.
- Fitness-Calmar Spearman correlations near zero or negative in most niches; especially NICHE-0011 -0.373 and NICHE-0013 -0.320. Requires tracing actual fitness source and metric definitions. No conclusion of implementation bug yet.
- P0 remains IN PROGRESS; P1-P7 OPEN/PARTIAL as described above. A/B/C trajectory analysis and decision replay have NOT yet run across all 13 niches.

## P0 CODE TRACE FINDINGS (2026-10-20)
- optimizer_v3.py fitness = cagr_diagnostic - 0.60*abs(mdd_diagnostic) - 0.40*max(0,abs(mdd_diagnostic)-0.20), with 0.03 penalty if zero fills. NOT Calmar fitness.
- guarded_evaluator_niche_single_exit.py labels portfolio basis cash-constrained realized/mark-to-market; shadow objectives are explicitly noncomparable to portfolio PnL. Verify exact production evaluator path before asserting full parity.
- pareto_breeding.py objective mixes portfolio CAGR, signed MDD, shadow expectancy and shadow tail; nondominated sorting is GLOBAL across all 13 niches, with niche quotas afterward. This does not implement independent niche-specific Pareto optimization.
- Next: reproduce rankings under within-niche Pareto and portfolio-only objectives, inspect tail direction, compare baseline policy on actual ledger. No production mutation.

## P0 CORRECTION IMPLEMENTED IN ISOLATED RESEARCH MODULE (2026-10-20)
- New niche_portfolio_pareto_v1.py: within-niche nondominated sorting on actual portfolio CAGR and signed MDD only; excludes invalid/zero-fill evaluations. No shadow-trade or cross-niche dominance.
- test_niche_portfolio_pareto_v1.py PASS: niche isolation, dominance, zero-fill exclusion, shadow-score independence.
- IMPORTANT: replacement ranking module is not yet wired into production breeder, has not been run through full GA evaluator, and has no demonstrated CAGR/MDD improvement. Existing production optimizer and checkpoint remain untouched/paused.
- Next: replay original candidate population with both ranking systems; then integrate into versioned research runner and test breeding, checkpoint, portfolio parity and all 13 niches before any production replacement.

## PRIMARY SUCCESS CRITERION REAFFIRMED (2026-10-20)
- Ultimate purpose is discovery/evolution of BETTER NEW chromosomes, not merely reranking the existing bank. Compare matched-seed, matched-evaluation-budget offspring from original versus corrected breeder, independently in all 13 niches.
- Primary economic outcomes: out-of-sample net CAGR, net trade expectancy/profit, maximum drawdown, catastrophic losses; secondary: success rate, trade count, upside retention, capital use, diversity and robustness. High win rate alone does not imply profitability.
- Include A/B/C trajectory-specific prediction and conditional management genes in chromosome evolution; retain time-t chronology, real cash-constrained ledger, fixed costs and blind governance.
- No claim of improvement until new offspring outperform baseline on properly held-out tests.

## EVOLUTIONARY BREEDER IMPLEMENTED AND UNIT TESTED (2026-10-20)
- niche_portfolio_breeder_v1.py selects niche-local parents by within-niche portfolio CAGR/MDD Pareto ranking, mates only within same niche, and maintains all 13 niche quotas.
- test_niche_portfolio_breeder_v1.py PASS: real genome crossover/mutation, 52 unique population, four chromosomes per each of 13 niches, 25 gene patterns, zero cross-niche mating. Test evaluation metrics synthetic, not real portfolio replay.
- Full research runner integration, matched-budget original-versus-corrected evolutionary comparison, A/B/C features, time-t and portfolio evaluation remain OPEN. Do not resume production checkpoint.

## MATCHED BREEDING CHECKPOINT COMPARISON (2026-10-20)
- Script: matched_checkpoint_breeder_comparison.py. Artifact: dev79_niche_origin_500x1000_20261019/all13_niche_screen/all13_fitness_firstwave/matched_checkpoint_breeder_comparison.json.
- Generation 122 checkpoint 500 members; 363 cached evaluations matched exact data/policy/code keys; compared same 363 evaluated parents with same RNG seed and 500 offspring per method.
- Original 387 novel / 113 retained, corrected 422 novel / 78 retained, 54 common offspring, all 13 niches represented. Corrected quotas 38-39 per niche; original 36-49.
- This is a breeding-only structural result, NOT offspring profitability, fitness advantage, or certification. Evaluate new offspring on real portfolio ledger and compare across chronological out-of-sample folds next.

## MATCHED OFFSPRING REAL-LEDGER EVALUATION LAUNCHED (2026-10-20)
- RUNNING process PID 433741: /opt/mts/ga5_redesign/evaluate_matched_offspring_all13.py, 8 workers, 808 unique novel offspring from matched parent pool, all 13 niches. Output: dev79_niche_origin_500x1000_20261019/all13_niche_screen/matched_offspring_portfolio_20261020/.
- Correct original baseline is pareto_trade_objectives.breed_pareto with fitness_niche_loss_control.fitness, using guarded_evaluator_niche_single_exit; earlier runner_unified.py audit applies to a DIFFERENT runner and must not be represented as exact paused-run code.
- This is a retrospective DEV79 matched-offspring comparison, not blind/out-of-sample certification. No production checkpoint changes.

## MATCHED OFFSPRING PORTFOLIO RESULTS COMPLETE (2026-10-20)
- 808/808 novel evaluations finished, exit code 0, runtime 1307.77s, 8 workers. Artifacts: dev79_niche_origin_500x1000_20261019/all13_niche_screen/matched_offspring_portfolio_20261020/{novel_evaluations.jsonl,all13_offspring_portfolio_comparison.csv,all13_offspring_summary.csv}.
- Corrected breeder achieved higher best CAGR in 10 of 13 niches; original wins niches 0005,0009, corrected niche 0012 only marginal improvement. Peak corrected CAGR 14.101% versus original 13.4448%. Corrected median MDD worse in every niche; many ~3% CAGR near cash yield. This does NOT establish higher risk-adjusted performance or out-of-sample robustness.
- Next priority: analyze trade-active candidates separately from cash-like zero-trade candidates; enforce minimum fills, positive net expectancy and per-niche DD constraints, measure Calmar without zero-DD cash distortions, then develop A/B/C predictive genes and run prospective chronological validation.
