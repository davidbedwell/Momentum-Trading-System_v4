# MTS G3 Specialist Discovery — Implementation Specification Candidate
Date: 2026-10-06
Status: DESIGN ONLY — NOT FROZEN FOR PRODUCTION
Depends on: MTS_G3_SPECIALIST_DISCOVERY_FREEZE_CANDIDATE_20261006.md

## 1. Architecture
G3 is a specialist opportunity discovery system, not a portfolio optimizer.

Pipeline:
DATA -> OPPORTUNITY SPECIALIST EVOLUTION -> EVIDENCE RECORD -> QD ARCHIVES -> SCOPE FREEZE -> TRANSPORT VALIDATION -> PORTFOLIO-ELIGIBLE LIBRARY -> SEPARATE ALLOCATOR EXPERIMENT.

Portfolio CAGR/MDD is unavailable to evolutionary fitness.

## 2. Candidate genome boundary
A genome SHOULD encode:
- applicability gate;
- opportunity/stock-selection expression;
- direction policy;
- entry rule;
- horizon and/or path-dependent management;
- add/reduce/exit/abandon/profit-realization rules;
- optional uncertainty/downside self-estimates only if independently calibrated.

A genome MUST NOT encode:
- portfolio slot count;
- portfolio sector weights;
- diversification targets;
- portfolio SAFE fraction;
- portfolio CAGR/MDD objective;
- specialist-to-specialist capital allocation.

Exact primitive grammar remains open pending audit of reusable G2 primitives.

## 3. Feature families available for consideration
Feature exposure is broad but causal-in-time:
- price/returns;
- volume/liquidity;
- volatility/range;
- trend/geometry;
- relative strength;
- market breadth/state;
- sector/peer state;
- earnings/fundamental fields with verified publication availability;
- rates/credit/external-market data only when PIT provenance exists.

Named strategy families are not genome targets.

## 4. Evidence record per fired opportunity
Required immutable fields:
- run/genome/version IDs;
- ticker and PIT universe membership;
- decision timestamp;
- all feature provenance timestamps;
- declared direction;
- entry timestamp/price convention;
- every management action;
- costs/slippage;
- exit timestamp/reason;
- gross/net return;
- MFE/MAE and timestamps;
- holding duration;
- return path or deterministic pointer to reconstruct it;
- market/sector/context descriptors;
- residualized outcomes under frozen control model;
- scope metadata;
- cluster/episode ID for dependence-aware statistics.

## 5. Archive state machine
EXPLORATORY/MUSEUM:
Behaviorally novel. No claim of economic validity.

CANDIDATE:
Passes minimum discovery evidence floor on permitted development data. Scope becomes immutable before any transport data is exposed.

TRANSPORT-VALIDATED:
Passes pre-registered transport/null/placebo/uncertainty gates within declared scope.

PORTFOLIO-ELIGIBLE:
Transport-validated and passes actionability/cost/capacity requirements. Eligible for separate allocator research.

RETIRED/QUARANTINED:
Later evidence indicates decay, provenance defect, implementation defect, or scope violation.

No backward mutation of a validated genome. Any change creates a new genome/version requiring new evidence.

## 6. Quality-diversity design
Maintain at least:
A. promoted quality-diversity archive;
B. novelty archive;
C. museum archive.

Behavioral signature should derive primarily from observed action/opportunity/outcome trajectories, not named strategies.

Candidate signature components:
- sparse vector/hash of dates and stocks fired;
- direction;
- normalized return-path representation;
- MFE/MAE path;
- holding duration;
- action sequence;
- market/sector state at firing;
- opportunity overlap/correlation with other organisms.

Embedding choices to compare cheaply before production:
- deterministic engineered signature baseline;
- PCA/random projection baseline;
- learned autoencoder/contrastive embedding if justified;
- CVT/adaptive clustering.

Do not adopt learned embedding merely because it is sophisticated. It must demonstrate stable neighborhoods and useful diversity under perturbation.

## 7. Local quality within niches
Local quality must not be whole-portfolio CAGR/MDD.

Candidate dimensions:
- reward distribution;
- downside/tail/MAE distribution;
- capital duration.

Use uncertainty-aware comparisons. Exact method remains to freeze after simulation study:
- confidence-bound dominance;
- Bayesian posterior dominance;
- bootstrap probability of dominance.

Frequency, correlation, scope width, capacity, cost sensitivity, and stability remain retained descriptors unless explicitly promoted to objectives after review.

## 8. Minimum validity floor
Before a genome can become CANDIDATE, require all of:
- minimum independent evidence count appropriate to claimed scope;
- positive evidence beyond matched null/placebo threshold;
- cost-aware actionability;
- no single ticker/episode domination above pre-approved concentration threshold unless scope explicitly claims it;
- stability to small parameter/input perturbations;
- no provenance/leakage violation;
- uncertainty interval reported.

Exact numeric thresholds are not yet frozen and must be calibrated from null experiments, not selected because real-data winners pass them.

## 9. Scope declaration
Scope is generated from permitted development evidence, then frozen.

Scope grammar may include:
- direction;
- sector/industry;
- market regime descriptors;
- volatility/liquidity range;
- event/fundamental state;
- price/volume state;
- duration class.

Scope complexity is logged and penalized in multiplicity accounting.

Post-hoc narrowing after transport results is forbidden. A revised scope creates a new hypothesis and new validation cycle.

## 10. Null program
Use multiple nulls because no single shuffle preserves all nuisance structure.

Candidate null family:
N1: within-ticker temporal block permutation preserving local return distribution/vol clustering while breaking feature->future linkage.
N2: cross-sectional date-wise outcome permutation within sector/liquidity buckets, preserving market-day structure.
N3: circular/large temporal shifts of feature/outcome alignment with guard bands.
N4: synthetic planted-signal calibration dataset to verify true positives remain discoverable.

The identical G3 machinery, budgets, archive rules, embedding, and promotion gates must run on null and real data.

Null calibration outputs:
- candidate count;
- archive occupancy;
- best apparent reward/downside/duration frontiers;
- false specialist survival by scope width;
- search-budget sensitivity;
- apparent transport rate under null;
- multiplicity-adjusted false-discovery estimate.

Production interpretation requires a frozen pass criterion before real validation is opened.

## 11. Multiple testing/search ledger
Every evaluated unique genome contributes to search effort.

Track:
- total unique genomes;
- total evaluations;
- mutations/crossovers;
- scope variants;
- restarts;
- embedding/QD variants tried;
- null variants;
- researcher-directed changes;
- G2-derived hypotheses.

Candidate statistical controls to compare:
- empirical FDR from matched-null pipeline;
- deflated performance statistics where assumptions fit;
- permutation family-wise/max-statistic controls;
- hierarchical FDR by behavioral cluster/scope.

Prefer empirical null calibration when analytic independence assumptions are implausible.

## 12. Transport validation design
Transport must match the claim.

General specialist:
- held-out names;
- held-out temporal blocks/regimes;
- dependence-aware uncertainty.

Sector/domain specialist:
- held-out names and periods within domain;
- negative/out-of-domain controls.

Rare episode specialist:
- episode-level validation;
- no multiplication of evidence by constituent stock-days;
- uncertainty explicitly remains large when episodes are few.

Validation data is loaded only after candidate genomes, scopes, archive status, code hashes, and thresholds are frozen.

## 13. Data partition principle
Do not allocate protected banks yet.

Before final freeze create a contamination map listing every ticker/time/data source touched by:
- Oct 1-6 research;
- G2;
- G2 null/calibration;
- prior crash research;
- fundamentals research.

Then designate:
- G3 design/training material;
- G3 transport material;
- final architecture comparison material.

Previously viewed history cannot become pristine by redownload.

Protected DEV50 remains untouched absent explicit governance change.

## 14. G2 relationship
G2 remains unchanged.

After G2 completes, preserve:
- all finalists;
- novelty archive;
- Pareto/island archives;
- surviving populations;
- checkpoints/intermediate elites where available;
- exact code/data hashes.

G3 Arm A: independent lineage.
G3 Arm B: G2-seeded lineage.
Optional Arm C: controlled hybrid.

Arm B/C ancestry is permanent metadata. G2-seen data cannot validate G2-derived lineages.

Before another large run, perform low-cost archaeology on G2 retained organisms using G3 behavioral signatures to estimate whether useful specialists already exist.

## 15. Conventional baselines
On identical permitted data/features:
- simple cross-sectional rank/factor baseline;
- regularized linear/logistic baseline where appropriate;
- gradient-boosted tree baseline or similarly strong conventional ML comparator.

These are controls, not new tuning playgrounds. Hyperparameter budgets must be logged.

## 16. Portfolio boundary
No allocator is built until a portfolio-eligible specialist library exists.

Future allocator input contract:
- active opportunity;
- specialist ID/scope;
- calibrated outcome distribution;
- uncertainty;
- downside/tail;
- expected capital duration;
- cost/capacity;
- covariance/overlap with other current opportunities;
- current holdings;
- SAFE/T-bill causal return.

Future allocator output:
- capital weights and/or no-trade decisions.

Sector concentration is permitted if evidence supports it; correlation/risk is measured rather than replaced by arbitrary sector caps.

## 17. Compute staging
Stage 0 — design and conformance: negligible compute.
Stage 1 — small synthetic/planted/null smoke tests.
Stage 2 — cheap embedding/QD method comparison on development subset.
Stage 3 — small matched real/null pilot with equal budgets.
Stage 4 — decision gate: does G3 distinguish real from null and beat simple baselines?
Stage 5 — only then authorize large discovery compute.
Stage 6 — transport validation after candidate freeze.
Stage 7 — allocator research only after validated library exists.
Stage 8 — untouched integrated G2 vs G3 architecture comparison.

A 64-core multi-hour run is prohibited before Stage 4 passes.

## 18. Stop conditions
Stop or redesign before expensive compute if:
- null archives look comparable to real archives;
- discovered specialists collapse after costs;
- evidence is dominated by one ticker/episode unintentionally;
- embedding/QD neighborhoods are unstable;
- simple baseline matches/exceeds G3 opportunity quality;
- candidate survival is highly sensitive to minor threshold changes;
- effective independent sample size is too small to support claims;
- validation barrier cannot be technically enforced.

## 19. Deliverables before production code
- contamination map;
- PIT feature/data manifest;
- genome grammar candidate;
- null specification;
- search-ledger schema;
- archive-state schema;
- behavioral-signature benchmark;
- statistical-gate specification;
- transport partition manifest;
- conformance test plan;
- compute budget;
- explicit approval/freeze record.

## 20. Design principle
G3 is not a machine for maximizing the prettiness of historical trades.

It is a controlled search for distinct, prospectively identifiable opportunity specialists whose evidence survives nuisance controls, uncertainty, multiplicity, realistic implementation, and transport.

Only after that raw material exists do we ask what portfolio can be built from it.