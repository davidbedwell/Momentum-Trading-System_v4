# MTS Stage 2 Corrected Preregistration V2 — 2026-10-07
Status: FROZEN BEFORE CORRECTED STAGE-2 OUTCOMES

## Supersession and quarantine
This protocol supersedes the abbreviated 128-candidate Stage-2 diagnostic and its dependent Stages 3-10. Those outputs are quarantined and MUST NOT influence this protocol's grammar, thresholds, ranking, promotion, budget, or conclusions.

## Evidence hierarchy
- DEV117: development/discovery universe for Stages 2-9.
- Recurring verification 50: the next 50 previously unseen stocks selected deterministically from the remaining Discovery pool; held-out transport/verification for each frozen stage. It may report transport but MUST NOT repair, tune, prune, mutate, rank, threshold, or architect any stage. Because it is reused, it is verification, not final blind proof.
- Fresh untouched 50: a different 50 previously unseen stocks from the remaining Discovery pool; do not select/open/access during Stages 2-9. Burn once only after integrated Stage 9 is frozen, as the first end-to-end blind checkpoint.
- Verification A then Verification B: remain untouched until after the integrated system passes the fresh-50 checkpoint; sequential final proofs with no post-blind repair.
- Cross-stock evidence does not create independent market-history episodes. Effective-independent evidence must be reported separately.

## Stage-2 scientific question
Discover causal stock-level LONG and SHORT opportunity chromosomes from the eight certified executable families and determine which individual genes, within-family combinations, and cross-family combinations have credible positive prospective net EV in which causal Planet/Sector/Galaxy environments.

## Certified vocabulary
MOMENTUM; BREAKOUT; TREND; MEAN_REVERSION; VOLATILITY; VOLUME_LIQUIDITY; RELATIVE_CROSS_SECTIONAL; MARKET_REGIME_STRUCTURE.
Recovered feature/parameter domains from Stage 0 are authoritative. EVENT_EARNINGS is excluded because it was not one of the eight certified executable families. CROSS_FAMILY_COMPOSITE is a new corrected Stage-2 composition layer over references to certified family predicates; the incomplete recovered cross-family resolver is not represented as previously executable.

## Chromosome semantics
A chromosome is a complete encoded hypothesis, not one indicator. It may contain 1-3 active predicates initially. Predicates reference certified family features plus causal parameters. Semantic mutations may add/remove/substitute a predicate, alter a parameter/state/direction, add/remove causal context conditioning, or alter composition. Semantic crossover exchanges compatible predicates/parameters; invalid combinations are rejected.
Cross-family compositions begin with AND/CONFIRMATION/CONTEXT_FILTER semantics. Complexity expands only when calibrated evidence shows incremental transferable information/EV over simpler parents.
Galaxy and Sector state are evidence/conditioning, never hard permission gates. No rule may encode Market Down => no LONG or Market Up => no SHORT.
forward_horizon is an outcome-measurement/path-characterization dimension only, never a mandatory holding period, timeout, or position-age rule.

## Search order
1. Single-predicate baseline sweep across all certified features and independent LONG/SHORT directions.
2. Planted-signal calibration at +0.25%, +0.50%, +1.00%, +2.00% effects using deterministic causal injections, measuring recovery power, false positives, runtime, and effective N.
3. Null calibration using outcome-preserving/permuted controls appropriate to serial market data. Record candidate-level null and periodic full-search null.
4. Calibration chooses evaluation budget and justified maximum complexity. Budget MUST NOT be selected from the invalid 128 run, old GA0 runtime, desired ETA, disappointment with results, or downstream outcomes.
5. Independent seeded GA populations evolve chromosomes. Baseline mechanics: population=32, elite=6, tournament=3, mutation=.20, crossover=.80. Number of populations/generations/evaluations is calibration-selected.
6. DEV117 frontier freezes before scoring the next-unseen Discovery verification-50. Verification results cannot alter the DEV117 bank.

## Economics and loss
Scientific evidence and economic utility are separate scores.
Economic EV uses the user-approved MTS_COST_MODEL_APPROVAL_FREEZE_20261006 cost model: commission 0; causal HLC spread proxy floor 2 bps/cap 50 bps; market impact 10 bps*sqrt(order_notional/trailing20 ADV); historical regulatory sale fees; SHORT borrow baseline 0.3% annual with 1%/3% sensitivities; calendar-day accrual. Five-bps one-way remains a reporting sensitivity.
Promotion requires credible EV_net > 0 and economic significance relative to costs; the previously agreed prospective-entry reference EV_net >= 2x expected transaction costs is reported/applied as an economic significance gate, not confused with EV>1.
For every chromosome retain win rate, average/median win, average/median loss, payoff ratio, tail loss/CVaR, MAE, return distribution, raw N, effective-independent N, uncertainty interval, recurrence through time, stock/sector/era concentration, and transport. SHORT loss/cost distributions are evaluated independently, not mirrored from LONG.

## Evidence and ranking
No arbitrary top-N survival cutoff. Every chromosome clearing frozen promotion criteria survives.
Rank survivors within appropriate categories: LONG vs SHORT; family; cross-family composite; discovered causal Galaxy/Sector/Planet environment; broad vs sector-specialist where supported.
Maintain separate scientific-evidence and economic-utility rankings.
Scientific evidence considers uncertainty, effective N, temporal recurrence, stock/sector recurrence, null comparison, stability, and incremental contribution/complexity.
Economic utility considers prospective net EV, loss/tail distribution, payoff asymmetry, opportunity frequency, costs, and capital-use descriptors without portfolio optimization.
Sector evidence is stratified/reported so one large sector cannot masquerade as independent broad recurrence. Legitimate sector specialists remain eligible and are labeled/ranked as specialists rather than discarded.

## Prohibited Stage-2 objectives
No CAGR/MDD optimization. No portfolio allocation/sizing. No lifecycle management. No fixed holding period. No ticker-specific/calendar-date rules. No use of recurring verification-50 outcomes for repair. No fresh-50/A/B access. No search-space enlargement because results disappoint.

## Gates and automation
Calibration gate: planted ladder recovery and null behavior must demonstrate adequate power and a defensible budget. If Thunder-6 is impractical, create a complete deterministic 64-vCPU handoff package, durability-verify it, enter WAITING_FOR_COMPUTE_PROVISIONING, and STOP. The controller may not provision paid compute.
Stage-2 PASS requires at least one preregistered category with credible promoted survivor(s), all required calibration/null/effective-N/loss evidence, no protected evidence access, deterministic replay, and verification-50 report generated only after DEV117 freeze. Scientific FAIL => STOP_SCIENTIFIC with no retune. AMBIGUOUS => STOPPED_REVIEW.
PASS => FREEZING => Git commit/push + independent remote SHA verification + Backblaze upload/inventory/check => Stage 3 automatic start.
Stage 3 may consume only the frozen Stage-2 bank and development evidence allowed by this hierarchy.

## Compute/reproducibility
Use all appropriate Thunder CPUs. Parallelism is engineering-only and must be proven output-equivalent to serial execution under fixed seeds. Prefer spawn/forkserver semantics over unsafe fork from multithreaded parents. Persist seeds, lineage, genome hashes, population/frontier checkpoints, scientific-config hash, input hashes, runtime calibration, and heartbeat/status.

## Calibration implementation amendment — frozen before corrected search outcomes
Matched-search calibration, not arithmetic effect recovery, is controlling. A deterministic certified predicate is planted into the 20-session outcome at 0%, +0.25%, +0.50%, +1.00%, +2.00%; five otherwise matched GA searches receive 2,000 evaluations each and are run in parallel. Recovery requires the planted predicate to appear in the top-20 frontier and its LCB95 to exceed both zero and the matched-null best LCB95. Production evaluations per independent population are selected prospectively from the smallest recovered effect: 0.25%=>8,000; 0.50%=>10,000; 1.00%=>15,000; 2.00%=>20,000; none=>STOP_SCIENTIFIC_CALIBRATION_FAIL. Four LONG and four SHORT independent populations are required. This amendment replaces the rejected arithmetic-only calibration implementation; no corrected production outcomes were inspected before this freeze.
