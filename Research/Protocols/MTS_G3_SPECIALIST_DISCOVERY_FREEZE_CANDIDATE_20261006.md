# MTS G3 Specialist Discovery — Experimental Freeze Candidate
Date: 2026-10-06
Status: DESIGN CANDIDATE — NOT FROZEN, NOT APPROVED FOR COMPUTE
Branch: research/g3-specialist-discovery-design

## 0. Purpose
G3 tests whether discovering and validating specialist opportunity organisms before portfolio construction can produce better raw trading material than optimizing a complete portfolio directly.

This is a hypothesis, not an assumption. G2 remains the integrated-strategy control.

G3 MUST NOT be launched until this protocol is reviewed, amended as needed, explicitly approved, and converted into an executable conformance manifest.

## 1. Primary scientific question
What prospectively observable combinations of market, sector, company, price, volume, and point-in-time fundamental conditions identify repeatable and transportable stock-return opportunities, and what causal-in-time entry/management behaviors produce robust reward–downside–duration tradeoffs from those opportunities?

G3 makes claims of prospective association and robustness. It MUST NOT claim observational discoveries are causal merely because they precede returns.

## 2. Core hypothesis
Portfolio-level CAGR/MDD optimization can extinguish organisms that contain useful, complementary, narrow-domain, or low-frequency opportunity expertise but are mediocre standalone portfolios.

G3 therefore tests:
1. whether such specialist opportunity organisms can be discovered under controlled false-discovery procedures;
2. whether their claimed behavior transports;
3. whether a later allocator using validated specialists improves genuinely held-out portfolio CAGR/MDD relative to integrated G2.

Failure to beat G2 on untouched evidence falsifies the practical advantage of the specialist architecture, even if interesting specialists are discovered.

## 3. Unit of evolution: Opportunity Specialist
The primitive organism is NOT a portfolio and NOT a context-free predictor.

An Opportunity Specialist contains:
- applicability/gating expression using only information available at decision time;
- stock/opportunity selection expression;
- direction: long, short, or conditional;
- causal-in-time entry behavior;
- horizon and/or path-dependent management;
- add/reduce/abandon/profit-realization/exit behavior where applicable;
- formal declared scope once promoted beyond exploratory discovery.

It does NOT contain:
- whole-portfolio diversification policy;
- sector allocation targets;
- portfolio SAFE allocation;
- portfolio-level CAGR objective;
- portfolio-level MDD objective;
- meta-allocation among specialists.

This boundary is mandatory. Position management needed to exploit one opportunity belongs inside the specialist. Capital competition among simultaneous opportunities belongs downstream.

## 4. Discovery is not category-driven
G3 MUST NOT predefine specialist classes such as momentum, mean reversion, recovery, short, technology, energy, sector rotation, or crash specialist as evolutionary targets.

Human-readable labels may be assigned only after behavioral evidence exists.

The architecture may expose causal primitives/features, but it MUST NOT require organisms to fit a named trading style.

## 5. Opportunity-level outcomes
For every fired opportunity, preserve the complete causal outcome path needed to reconstruct:
- net return under the specialist's management;
- MFE and MAE;
- tail loss;
- time to profit and time to failure;
- holding/capital duration;
- realized path shape;
- turnover and modeled costs;
- entry/exit/add/reduce events;
- contemporaneous market/sector/peer state;
- opportunity density and overlap with other specialists.

Raw opportunity records are immutable evidence artifacts.

## 6. Quality and Pareto treatment
No single scalar such as EV, Sharpe, CAGR, or win rate defines specialist quality.

Primary exploitation tradeoff axes:
- reward;
- downside/tail/MAE;
- capital duration.

These are plural objectives. Preserve uncertainty-aware non-dominated alternatives rather than selecting one universal optimum.

Estimated quality MUST carry uncertainty. Apparent dominance based on noisy point estimates is prohibited. Dominance/selection rules must incorporate bootstrap/posterior uncertainty or another pre-approved uncertainty-aware method.

Additional retained descriptors include:
- frequency/opportunity density;
- win/loss distribution;
- skew and tails;
- MFE/MAE distributions;
- turnover/cost sensitivity;
- capacity proxy;
- market/sector/regime dependence;
- stock breadth;
- stability under small perturbations;
- residual correlation / overlap with other specialists;
- estimation uncertainty.

These descriptors are evidence, not automatically optimization objectives.

## 7. Residualization and cheap-beta controls
G3 MUST distinguish stock-selection/opportunity information from trivial market, sector, size, or known-factor exposure where appropriate.

Each promoted specialist must report:
- raw outcome;
- relevant market/sector-relative outcome;
- residualized outcome under the approved factor-control model;
- whether its edge disappears after controls.

Residualization is diagnostic evidence and MUST NOT silently redefine every specialist's economic payoff.

## 8. Quality-diversity architecture
G3 should use quality-diversity / novelty preservation rather than CAGR/DD islands.

Behavioral niches MUST NOT be fixed solely by hand-authored trading categories.

Preferred design:
- high-dimensional behavioral signature derived from actual action/opportunity/outcome trajectories;
- learned or adaptive embedding/clustering;
- adaptive partitioning (e.g. CVT/adaptive MAP-Elites or justified equivalent);
- periodic re-clustering;
- explicit novelty channel;
- an unclassifiable/sparse-region mechanism;
- museum archive for behaviorally distinct organisms below current promotion quality.

Interpretable descriptors are retained alongside learned descriptors.

The learned embedding itself is a model and MUST be versioned, frozen per experiment, trained only on permitted development data, and audited for instability.

## 9. Minimum archive validity floor
Diversity alone is not usefulness.

Entry to the promoted specialist archive requires a pre-registered minimum validity floor based on evidence quality, sample adequacy, cost-aware outcome behavior, and null/placebo comparison.

The museum archive may retain novel failures or weak organisms for later scientific re-evaluation, but museum membership conveys NO trading validity.

Archive membership types must be explicit:
- exploratory/museum;
- candidate;
- transport-validated;
- portfolio-eligible.

## 10. Scope and narrow specialists
A candidate's claimed scope MUST be frozen before transport testing.

Scope may include market state, sector/domain, liquidity/volatility range, event type, direction, and other prospectively observable applicability conditions.

Narrowness incurs:
- explicit complexity/multiplicity accounting;
- a requirement for sufficient independent evidence within the claimed scope;
- out-of-domain negative controls where scientifically appropriate.

A narrow specialist is not required to work outside its declared domain.

Evidence standards are not lowered merely because an event is rare. Rare-event specialists may remain promising but uncertain when history cannot support high confidence.

## 11. Effective sample size
Rows/trades/stocks MUST NOT be treated as independent when driven by shared market episodes.

Validation reports must estimate evidence at the appropriate independence level:
- generalists: held-out stocks plus non-overlapping temporal/regime evidence;
- sector specialists: held-out names and time within claimed sector/domain;
- crash/stress specialists: independent episodes;
- clustered simultaneous signals: cluster/episode-aware uncertainty.

Pseudo-replication is a protocol violation.

## 12. False-discovery / null calibration — hard gate
Before production interpretation, the identical G3 discovery machinery MUST be run on matched null data in which predictive linkage is destroyed while preserving nuisance structure as much as possible.

Null design must preserve, as appropriate:
- cross-sectional distribution;
- volatility heteroskedasticity;
- missingness;
- sector/market structure;
- opportunity frequency;
while breaking the candidate predictive relationship.

Also require placebo/permutation controls for promoted specialists.

The null pipeline measures how many impressive specialists G3 manufactures from non-predictive data.

A production G3 run cannot be interpreted unless null behavior is below a pre-approved false-discovery threshold.

Multiplicity accounting must reflect the total search effort: organisms evaluated, scopes attempted, generations, restarts, G2-derived hypotheses where applicable, and researcher-directed retries. Reporting only finalist count is prohibited.

## 13. Data governance
A fresh yfinance download does NOT make previously observed history pristine.

Pristine means not used by the relevant adaptive research process.

Canonical price/volume and PIT universe data should be immutable and hash-addressed. Re-download only for data repair/provenance, not cosmetic re-pristining.

Quarterly fundamentals may be used only with verified historical availability timestamps. Fiscal period end is NOT assumed to equal public availability date.

Options data is EXCLUDED from G3 Phase 1 unless a separate audit establishes historically complete, point-in-time, survivorship-safe option-chain data. Options as execution instruments are a separate future experiment.

Existing protected banks remain governed by their prior restrictions. DEV50 remains preserved, not pristine, and is not opened for G3 design/tuning without an explicit governance change.

## 14. Discovery arms
The design should support three explicitly labeled conditions, but they need not all be run if compute-value analysis rejects one before freeze:

A. PRISTINE/INDEPENDENT ARM
- no G2 genomes as seeds;
- broad primitive/genetic diversity only.

B. G2-SEEDED ARM
- selected G2 archive/novelty organisms may seed hypotheses;
- all ancestry labeled;
- cannot claim validation on any data G2 previously used adaptively.

C. HYBRID ARM (optional experimental condition)
- controlled, auditable gene flow between independent and G2-derived lineages.

Any comparison must use matched compute budgets and identical downstream validation.

G2 is the integrated-strategy control, not assumed inferior.

## 15. Costs, capacity, and actionability
Discovery cannot ignore implementation.

Transaction costs/slippage and a capacity proxy enter opportunity-level characterization early enough to prevent phantom high-turnover edges from graduating.

However, costs MUST NOT be used to justify embedding whole-portfolio allocation back into specialist discovery.

Cost assumptions must be stress-tested across a pre-approved grid rather than represented by one convenient number.

## 16. Continual-market change
G3 is not assumed stationary forever.

Production design must eventually define:
- specialist health monitoring;
- evidence decay;
- re-validation cadence;
- retirement/quarantine rules;
- controlled re-discovery;
- versioning so live adaptation cannot rewrite historical validation.

These are downstream operational requirements and MUST NOT contaminate initial held-out tests.

## 17. Portfolio construction boundary
Only transport-validated specialists may become portfolio-eligible.

The downstream allocator receives simultaneous opportunity claims plus:
- uncertainty-shrunk return/outcome distributions;
- downside/tails;
- duration;
- costs;
- capacity;
- correlation/overlap;
- current holdings;
- causal SAFE/T-bill alternative.

The allocator may concentrate capital when evidence supports it. Arbitrary sector diversification is not imposed.

The allocator MUST account for winner's curse / estimation error. Raw highest estimated return is not sufficient for capital priority.

Portfolio construction is a separate frozen experiment. Specialist discovery cannot be retuned using its portfolio results without declaring a new adaptive research cycle.

## 18. Final comparison
The ultimate practical test is not whether G3 finds interesting specialists.

On genuinely untouched evidence compare:
- integrated G2;
- validated G3 specialist library + frozen allocator;
- simple approved baseline(s).

Primary final outcomes include CAGR, MDD, wealth, downside/tail behavior, robustness, and transport.

G3 wins only if the complete specialist architecture improves the relevant portfolio frontier on untouched evidence. Otherwise the added complexity has not earned itself.

## 19. Baselines
Before expensive production search, implement cheap controls:
- simple cross-sectional factor/ranking baseline;
- reasonable conventional ML baseline using the same PIT features and same permitted training data;
- null-data G3.

If G3 cannot materially exceed these on held-out evidence, complexity is suspect.

## 20. Prohibited shortcuts / protocol violations
- Optimizing G3 specialist survival directly on whole-portfolio CAGR/MDD.
- Using validation/blind outcomes to choose discovery organisms or tune niche definitions.
- Calling re-downloaded previously seen history pristine.
- Treating thousands of correlated stock-days as thousands of independent confirmations.
- Allowing source-island/archive status to substitute for receiving/archive evaluation.
- Declaring a narrow scope after seeing where a specialist worked.
- Quietly changing cost assumptions, factor controls, embedding model, archive thresholds, or scope rules after seeing validation.
- Letting G2 ancestry enter the independent arm.
- Treating museum novelty as evidence of profitability.
- Claiming causality from observational association.
- Launching large compute before executable null/conformance tests pass.

## 21. Required preflight tests before any large G3 run
1. Point-in-time feature availability / no-lookahead test.
2. PIT universe membership / survivorship test.
3. Fundamental publication-date causality test.
4. Opportunity path reconstruction test.
5. Add/reduce/exit lifecycle conformance test.
6. Cost/slippage application test.
7. Scope freeze and post-freeze immutability test.
8. Archive validity-floor test.
9. Learned-descriptor train/freeze/no-validation-leak test.
10. Null transformation invariants test.
11. Multiplicity/search-ledger completeness test.
12. Episode-aware effective-sample-size test.
13. Checkpoint/restart identity test.
14. Deterministic cache semantic-equivalence test.
15. G2-seed ancestry contamination test.
16. Independent-arm no-G2-gene-flow test.
17. Validation barrier test: all candidates frozen before protected data load.
18. Portfolio boundary test: no portfolio metric available to discovery fitness.

## 22. Search ledger
Every adaptive search must append to an immutable search ledger containing:
- run ID and code/data hashes;
- arm;
- seed/ancestry;
- population/generation/evaluation budget;
- number of unique organisms evaluated;
- scopes attempted;
- archive thresholds;
- descriptor/embedding version;
- null/real designation;
- researcher-directed restarts or parameter changes.

This ledger is part of the statistical evidence, not operational trivia.

## 23. Open decisions before freeze
The following are deliberately NOT decided in this candidate:
- exact genome grammar/primitives;
- exact learned behavioral embedding;
- exact QD algorithm;
- exact uncertainty-aware dominance rule;
- exact minimum validity threshold;
- exact multiplicity/FDR method;
- exact null transformation(s);
- exact factor residualization model;
- exact train/transport/blind partition assignment;
- exact compute budget and whether hybrid arm is worth it;
- exact downstream allocator.

These must be chosen before implementation and frozen before protected-data access.

## 24. Scientific interpretation
G3 is designed to reduce one failure mode—premature extinction of useful specialist raw material—while acknowledging the opposite failure mode: preservation of enormous amounts of sophisticated noise.

Therefore the central engineering problem is not merely diversity. It is diversity under strict false-discovery control.

The experiment is successful scientifically even if the specialist hypothesis fails, provided the protocol can tell us that cleanly.

## 25. Current authorization
AUTHORIZED NOW:
- design;
- critique;
- protocol refinement;
- non-compute-heavy inspection of existing development artifacts.

NOT AUTHORIZED:
- production G3 implementation;
- protected-bank access;
- large G3 evolutionary compute;
- changing G2;
- using G2/H.7 results to retroactively tune this protocol unless logged as a new design revision.

End of freeze candidate.
