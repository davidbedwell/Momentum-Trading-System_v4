# Competitive GA — Technical Design v1.0
Date: 2026-10-27
Status: DESIGN ONLY — implementation and scientific certification pending
Scope: GA6/GA7 competitive portfolio policy evolution with existing A_v2/B/B1/C + R-1 crash defense.

## A. Purpose and benchmark
Portfolio 1: $100k SPY buy-and-hold. Portfolio 2: $100k SPY plus same A_v2/B/B1/C + R-1 controller. Portfolio 3: $100k GA6/GA7 Competitive GA plus same controller. Primary evidence: P3-P2 incremental net terminal wealth and its stability; P3-P1 total value; compare CAGR, MDD, Calmar, Sharpe/Sortino, turnover, drawdown duration, exposure, cash drag, costs and concentration. Do not impose a 35% CAGR hard gate.

## B. Input contract (time-t only)
- Immutable GA6 and GA7 proposals: signal_timestamp, ticker, chromosome_id, family, native entry/exit/hold intent, native score and score provenance, eligibility and signal-specific metadata. GA6 and GA7 scores/EV units are NOT directly comparable.
- Causal point-in-time prices, corporate actions, sector, earnings embargo, eligible membership and market-wide features.
- Regime feature vector: breadth, market trend, realized volatility, momentum, dispersion and recovery indicators; do not use future-known crash labels.
- Shared versioned niche service: overlapping membership strengths, distances, radii and model training cutoff; only past-trained models.
- Current portfolio state: settled/unsettled cash, holdings, cost basis, unrealized P&L, holding age, risk usage, sector/correlation exposures, outstanding orders.
- Historical chromosome evidence only after outcomes become observable; no future trade P&L, hindsight selection, or in-fold future feature normalization.
- Controller: same authoritative A_v2/B/B1/C + R-1 state and execution timeline as defended SPY.

## C. Evolvable genome — bounded, interpretable typed grammar
1. Opportunity scoring: weighted normalized trend, relative strength, volatility, liquidity, breadth, native signal strength (family-calibrated), opportunity age and evidence confidence.
2. Chromosome reliability: causal historical hit/EV, sample-size shrinkage, recent degradation, family/niche specialization, disagreement/agreement among signals.
3. Regime conditioning: soft regime gates and piecewise conditional weights; crash defense cannot be overridden.
4. Niche conditioning: select/weight/combine existing memberships and niche distances; overlapping niches allowed; optional interaction terms with regime and chromosome identity.
5. Capital allocation: positive-score threshold, confidence scaling, target-weight schedule, cash reserve preferences; hard 10% symbol cap outside genome.
6. Position management: hold/add/reduce/exit thresholds, native exit priority, expected net advantage required to replace a holding, turnover hysteresis and minimum evidence.
7. Uncertainty and diversification: confidence penalties, covariance/sector sensitivity, disagreement and concentration preferences; external hard limits remain authoritative.

Represent each genome as versioned JSON with schema_version, typed modules, enabled features, bounded real-valued coefficients, discrete operators, conditional gates, mutation metadata, and stable hash. Reject invalid grammar, undefined features or unavailable-at-t inputs. Cap structural complexity and condition depth. Seed simple linear, threshold, interaction and regime-specialist templates; do not force family quotas.

## D. Decision algorithm per session
1. At close t reconstruct eligible PIT universe, regime/niches and current holdings.
2. Ingest GA6/GA7 native candidate intents. Deduplicate multiple chromosomes proposing same ticker while retaining attribution and disagreement.
3. For each candidate, score expected incremental benefit net of estimated execution/holding costs; score existing holdings under the same causal feature policy.
4. Generate target actions: hold/add/reduce/exit/replace/cash. A replacement must exceed the retained holding by a learned margin after costs; no forced replacement.
5. Apply independent defense overrides, entry embargo, max symbol 10% during learning, <=2% equity risk per trade, sector/correlation rules, cash/settlement and execution constraints.
6. Queue orders no earlier than next open. Execute deterministically; mark-to-market daily and persist accepted/rejected intents with reasons, fills, costs, NAV, drawdowns, attribution and exposure.
7. Mature shadow/counterfactual evidence only when an outcome is chronologically known; use it for later updates, never retroactively.

## E. Evolutionary process — initial defaults, tunable after audit
- Population 400 total; diverse initialization from all gene families and structurally different templates.
- Initial parent pool target 120, chosen by non-dominated sorting plus structural and behavioral novelty; preserve a small elite archive. No per-niche or per-GA-family quotas.
- Reproduction: approximately 50% crossover, 30% parameter mutation, 15% structural mutation, 5% independent immigrants; these are initial proposals, not measured optima.
- Mutations can enable/disable feature groups, add/remove bounded conditions, change weights, thresholds, regime/niche interactions and replacement margins.
- Fitness: full chronological shared-bankroll NAV replay. Pareto objectives: net excess terminal wealth vs defended SPY, maximum drawdown, and forward discovery-fold stability. Record CAGR, Calmar, tail loss, turnover, cost, exposure and complexity; use explicit validity gates for hard violations, insufficient observations and accounting errors.
- Early fidelity: deterministic syntax/causality checks, inexpensive fixture/small discovery-fold smoke, then complete full-fidelity replay for survivors. Cheap screening may never substitute for final evaluation.
- Max 300 generations for initial experiment, checkpoint every 10, report every 25, early stop after 75 generations without meaningful Pareto hypervolume or diversity progress after minimum 100 generations; review and adjust empirically. Avoid claiming convergence from single best score.
- Deterministic seeds, lineage, artifacts and resumability; parallelism bounded by available resources, not assumed.

## F. Discovery, niche and regime research
- Reuse and audit existing GA6/GA7 niche recognizer, PIT guard, membership reconstruction and feature ranks. Preserve overlapping memberships and a dominant membership only when explicitly useful.
- Shared niche-research extension proposes novel descriptive regimes, niche subdivisions, intersections, or drift indicators using only historical training slices; no profitability labeling baked into niche discovery.
- New niche candidates require chronological reconstruction and subsequent discovery-validation, incremental portfolio ablation against existing-only and no-niche alternatives, and versioned approval before the next GA cycle. Individual portfolio genomes do not rewrite niche definitions.
- Ablations: no regime/niche, existing-only, existing+new, GA6-only, GA7-only, combined deterministic, combined evolved.

## G. Scientific validation and iteration
- Chronological discovery-training and later discovery-validation folds, with embargo/purge for trade horizon and any overlapping labels; never random shuffle of dates.
- Select by aggregate forward discovery-validation and downside robustness, not peak in-sample CAGR; archive all attempted revisions and account for multiple testing.
- Each iteration: run -> independent audit -> trade/regime/niche diagnostics -> assistant hypotheses -> Claude/Grok adversarial review if accessible -> preregister 1–3 changes -> rerun same folds -> champion/challenger decision.
- Maintain versioned run manifest, hashes, seeds, code, chromosome sets, niche models, controller, market inputs, fills, NAV and raw review packets.
- Freeze code/config/selection and candidate policy BEFORE untouched DEV87 proof; do not repeatedly tune on DEV87.
- If full-fidelity forward discovery validation fails to exceed defended SPY and deterministic selector with acceptable risk, stop or redirect, not promote.

## H. Engineering gates
G0: audit actual GA6/GA7 source signals, historical chronology, niche recognizer and controller dependencies.
G1: complete shared event-driven kernel with correct T+1 settlement, dividends/splits, NAV, costs, fills, defense state and parity fixtures.
G2: deterministic combined selector and full daily ledger, benchmark 1/2 parity.
G3: genome grammar, evolutionary operators, selection, checkpoints and reproducible full-fidelity evaluation.
G4: discovery iteration + external adversarial review; freeze then DEV87 independent proof.

## I. Explicit exclusions
Not yet a live trading system. No guaranteed GA6/GA7 family allocations. No independent genome-level rewriting of niche models. No synthetic fitness substituting for full replay. No unverified performance claims or DEV87 tuning.

## J. Approved decision-flow correction: defense immediately after market state
Required logical sequence: (1) reconstruct causal market state at time t; (2) evaluate Risk + A_v2/B/B1/C + R-1 defense and establish allowed trading state, entry blocks, liquidation requirements, risk budgets and recovery permission; (3) generate/filter GA6 and GA7 proposals within that permitted state; (4) Competitive GA scores and allocates eligible opportunities, including holding/replacement decisions; (5) next-open execution independently rechecks defense, risk and cash constraints and accounts for fills/NAV. Defense is authoritative and cannot be bypassed by the Competitive GA. If defense requires liquidation, the system schedules the mandated exits even if there are no eligible entry proposals. Defense inputs and state must be causal, with no same-close decision executed retroactively at that close.
