# MTS G3 Production Specialist Discovery Protocol — Draft for Cold Audit
Date: 2026-10-07
Status: PROSPECTIVE DRAFT — V3 OUTCOME NOT CONSULTED — NOT YET EXECUTION FREEZE

## Purpose
G3 discovers a diverse bank of opportunity specialists. It is not a portfolio optimizer. Discovery fitness cannot access CAGR, portfolio MDD, slot count, sector target weights, SAFE allocation, or specialist-to-specialist allocation.

## Authorization
Engineering and conformance may proceed now. Large evolutionary compute may launch only from a machine-verified V3 PASS artifact whose protocol/hash checks pass. V3 FAIL or malformed/missing evidence fails closed. Protected transport/blind data remain inaccessible until candidate genomes and scopes are frozen.

## Independent arm first
Production run A uses only the independent G3 lineage. G2-derived genomes/labels/caches/portfolio outcomes are forbidden. G2-seeded Arm B is a later separately labeled experiment and cannot validate on G2-adaptive evidence.

## Genome grammar
An organism contains 2-8 modules. Each module contains:
- applicability expression: 1-4 causal feature predicates;
- opportunity expression: 1-6 causal feature terms with signed weights;
- direction policy: long, short, or conditional sign;
- entry threshold and confirmation persistence 1-5 sessions;
- lifecycle: take-profit 1-20%, stop-loss 0.5-12%, maximum horizon 2-60 sessions, add threshold 0.5-8%, reduce threshold 0.5-10%, trailing-profit retention 0-80%;
- optional abandon rule based only on causal feature deterioration.
Genome contains a module combiner and abstention threshold. No ticker identity, company identity, future regime label, calendar-year lookup, or portfolio-allocation genes are allowed. Sector/market state may enter only as causal observable features.

## Feature boundary
Only hash-manifested causal features available at the decision timestamp may be used. Phase-1 production grammar admits price/return, volume/liquidity, volatility/range, trend/geometry, relative-strength, market-state, peer/sector-state, and PIT earnings-event fields that pass publication-timing tests. Any field lacking verified PIT timing is excluded rather than imputed into eligibility.

## Opportunity evidence
Every firing stores ticker, decision time, feature provenance, direction, entry convention, every lifecycle action, gross/net return, MFE, MAE, tail loss, time-to-profit/failure, duration, turnover, costs, path signature, context signature, and episode/cluster ID. Costs are evaluated at 0/5/10/20/50 bps; archive quality uses 10 bps and must remain positive at 20 bps to promote.

## Search architecture
Eight independent evolutionary islands. Population 256/island. Maximum 200 generations. Islands evolve independently; migration every 20 generations moves behaviorally novel genomes only and migrants are re-evaluated completely under receiving-island semantics. Deterministic raw simulations may be reused only for identical genome/data/cost semantics. No source rank, feasibility, archive status, or objective treatment transfers.

Second consecutive plateau freezes that island and stops further evolutionary evaluation work there; freed worker capacity is reallocated to active islands without changing any population size, generation budget, objective, fitness, or genome. Checkpoint every generation. Resume must reproduce uninterrupted state hashes.

Variation: 55% mutation-only, 30% crossover+mutation, 15% fresh random immigrants. Structural mutations may add/remove/replace modules or predicates within grammar bounds. Numeric mutation is bounded and logged. No human-directed injection after launch.

## Multi-objective exploitation quality
No scalar master fitness. Selection uses uncertainty-aware Pareto treatment on:
1. net reward: cluster-bootstrap 10th-percentile lower confidence bound of mean net return/event at 10 bps;
2. downside: cluster-bootstrap 90th-percentile upper confidence bound of mean MAE plus 5% tail loss (minimize);
3. capital duration: cluster-bootstrap 90th-percentile upper confidence bound of mean holding sessions (minimize).
A dominates B only when it is no worse on all three uncertainty-aware axes and strictly better on at least one. Tournament selection first uses Pareto rank, then behavioral novelty, then lower uncertainty, never portfolio metrics.

Bootstrap unit is the machine-defined event cluster: signals whose forward paths overlap in time and share broad market exposure are one cluster. 500 deterministic bootstrap resamples per evaluated archive contender; cheap point estimates may screen ordinary population members, but no organism may enter the promoted archive without full uncertainty evaluation.

## Quality diversity
Production Phase 1 uses a deterministic engineered behavioral descriptor, not a learned embedding, to avoid adding an unfrozen representation model to the first production experiment. Descriptor components: firing density, stock breadth, long/short share, median duration, MFE/MAE ratio, return-path shape coefficients, action-sequence frequencies, market-state firing distribution, peer/sector-state firing distribution, and opportunity-overlap signature.

Descriptors are robust-scaled using development data only and frozen at launch. A deterministic 12-D random projection (seed 20261007) compresses the descriptor after scaling. CVT-MAP-Elites uses 256 centroids fit only on development behavior samples before the evolutionary run and then frozen. Maintain three separate archives: promoted QD, novelty, and museum. Museum membership conveys no validity.

## Minimum promotion floor
A genome can become CANDIDATE only if all are true on permitted discovery data:
- >=50 fired events and >=25 independent event clusters;
- 10-bps reward LCB > 0;
- point mean net return remains >0 at 20 bps;
- no single ticker supplies >50% of positive net PnL unless the prospectively generated scope is explicitly narrow before transport;
- perturbing every numeric threshold by +/-10% leaves median net reward positive in at least 75% of deterministic perturbation cases;
- no provenance/leakage violation;
- complete evidence record and search-ledger entry.
Narrow specialists may promote with <3 tickers only if their observable scope is frozen before transport; their evidence floor is not relaxed.

## Novelty and museum
Novelty archive retains the 512 most behaviorally separated feasible organisms regardless of profitability. Museum retains up to 1024 distinct organisms that fail promotion but occupy sparse behavioral regions. Promoted QD archive stores at most 4 non-dominated candidates per CVT cell, capped at 1024 total by uncertainty-aware Pareto rank then novelty.

## Scope generation and freeze
Scope is generated only from causal observable firing/context distributions on discovery data. Allowed scope dimensions: direction, sector/industry observable membership, market-state features, volatility/liquidity ranges, event/fundamental state, price/volume state, duration class. Scope complexity is logged. Candidate genome, scope, code hash, data hashes, descriptor transform, archive state, and thresholds are immutable before transport data can be loaded. Any later change creates a new candidate version and new validation cycle.

## Multiplicity
Every unique genome, scope variant, restart, descriptor variant, null variant, and researcher-directed revision is recorded. Production discovery reports empirical false-discovery burden from the already frozen matched-null gate plus max-statistic null calibration for archive promotion. No p-value shopping or unlogged restart is permitted. Search budget cannot increase after outcomes are observed.

## Compute budget and stopping
Hard maximum: 8 islands x 256 population x 200 generations = 409,600 island-individual generation slots before duplicate-cache savings. Early island plateau may reduce this. The budget may not be increased based on results. Full 64-core worker pool is used for organism evaluation; BLAS threads fixed to 1. Exact one-generation benchmark must be recorded before launch ETA is published.

## Output
Discovery ends with: promoted Pareto/QD archive, novelty archive, museum archive, immutable opportunity evidence, search/multiplicity ledger, checkpoint hashes, behavior descriptor manifest, candidate scope freezes, and a machine-readable transition artifact. It does not produce a portfolio.

## Downstream transition
If zero candidates pass promotion: STOP_G3_DISCOVERY_NO_CANDIDATES.
If >=1 candidates pass: freeze candidates/scopes and authorize transport-validation engineering/execution under protected-data barriers. Transport outcomes cannot mutate or repair candidates. Portfolio allocation remains a later separate experiment.
