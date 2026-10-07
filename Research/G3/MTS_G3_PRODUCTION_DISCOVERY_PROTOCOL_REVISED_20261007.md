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


# Prospective Audit Amendment A — 2026-10-07
Status: incorporated before V3 outcome was consulted.

## Parallel execution (Claude BLOCKER resolved)
The search is synchronous by generation. At each generation boundary, all organisms from all active islands are flattened into one immutable work queue and evaluated concurrently by a shared 60-process worker pool (4 CPUs reserved for OS/controller). Tasks share no mutable evolutionary state. Results are restored to deterministic island/population order before ranking/breeding. Frozen islands submit zero tasks; freed capacity therefore services active-island tasks without changing any island population or generation budget. This preserves the user's already-frozen second-plateau rule; Claude's alternative suggestion to spawn replacement islands or enlarge populations is explicitly rejected because it would violate that governance. Pre-launch benchmark must show >=80% aggregate CPU utilization during evaluation; otherwise STOP_PARALLEL_UTILIZATION_FAILED.

## Reachability pre-study
Before production launch, run a non-outcome structural reachability smoke on planted/development data using 2 islands x 20 generations and report unique genome rate, descriptor-space occupancy, and random-immigrant novelty. This cannot change production budget after real outcomes are seen. Failure threshold: <15% of the 256 frozen descriptor cells ever occupied -> STOP_SEARCH_REACHABILITY_FAILED and redesign before real production.

## Pareto pressure
Archive contenders use cluster-bootstrap bounds. Ordinary population selection uses deterministic point-estimate axes until contender status, avoiding universal rank-1 inflation from noisy bounds. At generation 10 report rank-1 fraction. If >90%, the prospectively frozen tiebreak order is Pareto rank -> lower uncertainty width -> novelty; otherwise Pareto rank -> novelty -> lower uncertainty width.

## Dependence clusters and bootstrap
The first production experiment uses a deliberately conservative market-dependence definition: any events whose holding intervals overlap by >=1 session belong to the same transitive connected component, regardless of ticker/sector. This assumes common market exposure rather than trying to estimate it. Promotion requires >=25 such clusters. Archive bounds use 2,000 deterministic cluster-bootstrap resamples seeded by SHA-256(run, genome). No event-level bootstrap may authorize promotion.

## Cost robustness
Promotion requires cluster-bootstrap reward LCB >0 at 10 bps and 15 bps, plus point mean >0 at 20 bps. Costs must be monotone in the simulator for an identical event/action path; a conformance test enforces this.

## Perturbation robustness
Perturbation is one-at-a-time: each numeric genome parameter is evaluated at -10% and +10% with all others fixed. At least 75% of the resulting 2N deterministic cases must retain positive median net reward at 10 bps.

## Survivorship and claim boundary
The recovered DEV80 panel is a predetermined design panel, not a point-in-time historical universe. It therefore cannot support a claim of survivorship-safe market-wide performance. Production discovery may use it only to generate hypotheses/specialists. Every promoted candidate is labeled DESIGN_PANEL_SURVIVORSHIP_EXPOSED. Portfolio eligibility is prohibited until transport validation uses a separately audited PIT universe including historical entrants/exits/delistings or an equivalently survivorship-safe source. No discovery result may erase this label.

## Scope generation
Scope boundaries may use only pre-frozen bins: sector/industry identity available at decision time, direction, and deciles of decision-eligible continuous features whose breakpoints are computed once from the designated descriptor-development interval before evolution. Firing profitability cannot move scope boundaries. Any narrower post-hoc scope is a new hypothesis/version.

## Data partition manifest
Within the independent DEV80 design panel, dates are split chronologically before evolution: first 20% descriptor-development only; middle 60% evolutionary discovery; final 20% internal temporal confirmation. A 60-session embargo separates discovery and temporal-confirmation evaluation. Descriptor scaling/CVT fitting use only the first 20%. Evolutionary fitness cannot read final-20% outcomes. Candidate structure/lifecycle/scope is frozen before internal temporal confirmation. This is internal development confirmation, not protected transport validation.

## Temporal stability
Within the 60% discovery interval, report three equal chronological thirds. Promotion to CANDIDATE requires positive point mean at 10 bps in at least 2/3 thirds and then positive cluster-bootstrap reward LCB on the frozen final-20% internal temporal confirmation. No mutation/ranking repair occurs after that freeze.

## Multiplicity / production null
V3 is a machinery-level real-vs-null gate, not sufficient by itself to estimate the false-discovery burden of the much larger production grammar. Before interpreting the production archive, run the identical production search machinery on pre-frozen within-stock 60-session stationary-block-bootstrap outcomes with identical budget and archive rules. The REAL and NULL production runs are separate labeled arms. No Real-selected genome, scope, rank, feasibility, descriptor cell, or archive state transfers to NULL. Production candidates must exceed the null-run max promoted reward-LCB threshold; if the null produces no promotable candidate, its maximum contender LCB is used. A second independent null realization is required as sensitivity. This is a 1 REAL + 2 NULL matched-budget program; budget cannot be increased after results. The exact benchmark projects all three arms before launch; if projected wall time exceeds 14 days, STOP_COMPUTE_INFEASIBLE rather than silently shrinking science.

## Restart/checkpoint
SHA-256 is mandatory. A resume loads the last valid generation-boundary checkpoint with identical code/config/data hashes and does not add multiplicity. Any changed seed/config/code/data or generation-0 relaunch is a restart/new experiment and is logged. Retain every 10th checkpoint plus the last 3 consecutive generation checkpoints; preflight fails if projected checkpoint storage exceeds 500 GB.

## Descriptor operational definitions
Return-path shape is five equally spaced cumulative-PnL samples normalized by absolute terminal PnL+1e-9. Action frequencies are counts/session for ENTER, HOLD, ADD, REDUCE, EXIT. Conditional direction is only sign(score) from the module's already-declared opportunity expression; it cannot add another hidden feature expression. Migration eligibility is distance to receiving-island nearest neighbor greater than the receiving population's median nearest-neighbor distance; receiving semantics fully re-evaluate the migrant before any admission.

## QD eviction / duplicate handling
Within a full cell, remove dominated organisms first; if all are mutually non-dominated, evict the organism with smallest within-cell nearest-neighbor descriptor distance. Cross-island behavioral duplicates are merged when scaled descriptor distance <=0.01 and fired-event Jaccard >=0.95; retain lower-uncertainty version and log merge.

## Wall-clock and evaluation safety
Per-organism hard timeout 120 seconds; timeout receives worst objective values and is logged. Total production program hard stop 14 days. Exact one-generation benchmark must demonstrate feasibility before authorization.

## Terminology
"Decision-eligible" means computed solely from information available by the decision timestamp. It makes no claim of economic causation.


# Prospective Audit Amendment B — 2026-10-07
Status: incorporated before V3 outcome was consulted.

## Operational plateau definition
Plateau is island-specific and evaluated only at non-overlapping 40-generation boundaries. The monitored metric is the island's deterministic exploitation-front hypervolume proxy computed from its non-dominated reward/downside/duration point-estimate front after fixed affine normalization from the descriptor-development interval. A 40-generation window is a plateau when end-window hypervolume improves <0.5% versus the start-window hypervolume AND the island adds zero new promoted-QD cells during that window. One plateau window records plateau_count=1. A second immediately consecutive 40-generation plateau window records plateau_count=2 and freezes the island. Any window failing either plateau condition resets plateau_count=0. A frozen island submits no further evolutionary evaluation work. This definition is immutable during the run.

## Frozen-island migration
Frozen islands neither send nor receive migrants. Their terminal population and archives remain immutable evidence. Active-island migration never changes population size. Migrants are re-evaluated under receiving-island semantics before admission; no source rank/feasibility/objective/archive status transfers.

## Internal temporal-confirmation failure
A frozen discovery candidate that fails the final-20% internal temporal-confirmation requirement is ineligible for CANDIDATE/promoted-QD status. It may be retained only in the museum/novelty evidence archive with status TEMPORAL_CONFIRMATION_FAILED. No repair, re-evolution, threshold adjustment, or scope narrowing is permitted.

## Null contender definition
For production-null max-stat calibration, a CONTENDER is an organism satisfying the event-count floor (>=50), independent-cluster floor (>=25), 15/20-bps cost screens, temporal-third consistency, perturbation robustness, provenance checks, and concentration/scope rules, but irrespective of whether its reward LCB is >0. For each NULL arm, the max-statistic is the maximum 10-bps cluster-bootstrap reward LCB among CONTENDERs. If no organism satisfies CONTENDER status, the null max-statistic is -infinity and this fact is reported. A REAL candidate must satisfy all ordinary promotion requirements and have 10-bps reward LCB strictly greater than the maximum max-statistic across both pre-frozen NULL arms.

## Clarifications
The 60-session embargo is excluded from both discovery and confirmation; chronological percentages define target source intervals before embargo removal and exact row counts are written to the partition manifest. Non-retained generation checkpoints are deleted only after the next retained checkpoint hash is verified. Duplicate merge is checked at archive insertion and migration admission. The 2-of-3 temporal-third test is discovery-interval only. Exact benchmark uses descriptor-development data and includes projected perturbation work. Positive profitable-event PnL concentration is direction-agnostic.

# User-Approved Prospective Amendment C — 2026-10-07
Status: APPROVED BEFORE ANY PRODUCTION G3 REAL OR NULL SEARCH EXECUTION.

## Production-null count reduced from two to one
The production program is amended from 1 REAL + 2 matched NULL arms to **1 REAL + 1 matched NULL arm**. The single production NULL uses the already specified within-stock 60-session stationary-block-bootstrap outcome transformation and must receive the identical evolutionary search budget, genome grammar, archive mechanics, temporal partitioning, promotion/contender rules, costs, perturbation rules, and compute treatment as REAL. No Real-selected genome, scope, rank, feasibility, descriptor cell, or archive state transfers to NULL.

Rationale: V3 separately tests whether the discovery machinery distinguishes Real structure from three preregistered null families. The production matched NULL has the narrower role of empirically calibrating the false-discovery/max-stat burden created by the much larger production grammar and adaptive search. One identically budgeted production NULL is sufficient for that role; a second full production NULL is not required.

The production NULL max-statistic is the maximum 10-bps cluster-bootstrap reward LCB among NULL CONTENDERs under the definition frozen in Amendment B. If no NULL organism reaches CONTENDER status, the null max-statistic is -infinity and that fact is reported. A REAL candidate must satisfy all ordinary promotion requirements and have 10-bps reward LCB strictly greater than this single matched-NULL max-statistic.

No other scientific search setting is changed by this amendment. The maximum evolutionary workload is therefore 409,600 generation-slots for REAL plus 409,600 identically budgeted generation-slots for NULL, before duplicate-cache savings and early island plateau freezes: **819,200 maximum total slots**. The exact benchmark projects both arms, not three. The existing 14-day hard program ceiling remains unchanged.
