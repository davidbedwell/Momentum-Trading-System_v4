# MTS v4 Cross-Sectional Research and Derived Market Store Design

Status: HUMAN-APPROVED DESIGN — 2026-09-14

This document records the approved extension of MTS v4 from subject-by-subject research into a dual-mode research system that preserves sequential subject research while adding deterministic universe-level analysis when the scientific question requires it.

## 1. Governing intent

MTS remains an AI-directed scientific research system. Sol/Qwen choose scientific questions, hypotheses, methods, parameters, interpretations, and continuation. Deterministic code provides reproducible acquisition, feature construction, execution, lineage, point-in-time integrity, caching, and persistence.

Single-ticker research remains valid and useful. It is not being replaced. The system adds universe/cohort research so a valid scientific question is never rejected merely because its evidence spans more than one security.

The AI must never receive millions of market rows merely because Analysis used them. AI requests the experiment; deterministic Intake/Analysis performs row-level work; AI receives compact governed evidence.

## 2. Approved Nexus boundary extension

The human explicitly approves one durable-data extension to the original v4 Nexus boundary:

- raw or otherwise reacquirable source data such as OHLCV remains temporary campaign/update cache data and is not durably warehoused in Nexus;
- reproducible **derived point-in-time market state** may be retained durably inside the Nexus-owned derived market store because it is a compact, reusable scientific substrate whose repeated reconstruction would waste time and compute;
- significant findings, hypotheses, research state, lineage, failures, and scientific memory continue to live in Nexus as before.

The derived market store is therefore part of Nexus, but is physically separable from the small JSON scientific-memory document so a large columnar dataset does not bloat or corrupt normal Nexus metadata operations.

## 3. Three durable/ephemeral layers

### 3.1 Temporary raw/update cache

Contains reacquirable raw source data used by an active research or maintenance campaign. It persists for the full AI research session when reuse is useful, expands only when necessary, and is deleted when the campaign/update no longer needs it.

### 3.2 Nexus derived market store

Contains point-in-time derived measurements and universe state suitable for repeated deterministic research queries. Historical values are append-only by effective date under normal operation. New market sessions create new rows rather than mutating prior observations.

### 3.3 Nexus scientific memory

Contains scientific findings, hypotheses, research-state records, result/evidence lineage, negative results, validation state, and compact context for future Research Director reasoning.

## 4. Research scopes

Every Analysis request must be representable as one of the following scopes:

- SUBJECT — one security/subject;
- UNIVERSE — a defined eligible population, such as a point-in-time S&P 500 universe;
- COHORT — an AI-specified subset of a universe;
- EVENT_COHORT — a population of security-events such as earnings announcements.

Backward compatibility is required. Existing single-subject runners continue to operate unchanged in scientific meaning. Generic validation/compiler/orchestration must not reject evidence merely because more than one subject participates in an explicitly declared non-subject scope.

## 5. Point-in-time universe integrity

No historical cross-sectional test may project today's index members backward through time.

A universe definition must identify the membership source and whether point-in-time membership is required. Derived rows must be interpretable against the eligible population at the observation date.

Stable security identity must be distinct from ticker. Ticker is a time-varying attribute. Future work may add identifier mappings for mergers, ticker changes, share classes, spinoffs, and delistings without changing the research-scope contract.

If point-in-time membership is unavailable, the system must label the limitation explicitly rather than silently substitute current membership.

## 6. Derived feature design

Precompute measurements, not conclusions.

Useful reusable families include:

- trailing returns and return structure over multiple windows;
- trend relationships, slopes, acceleration, distance from trend;
- ATR, normalized ATR, realized volatility, volatility state;
- volume, relative volume, turnover, participation state;
- range location, breakout/breakdown state, drawdown and extension;
- candle/gap structure;
- momentum and oscillator measurements;
- cross-sectional ranks/percentiles;
- sector/industry-relative measures;
- breadth and market-regime descriptors;
- earnings/event context and event-relative indexing when point-in-time timing is defensible;
- historical forward outcomes used only by exploratory/retrospective scientific analysis.

Human risk horizons such as 1/3/5/10/20 trading days are not the scientific discovery boundary. AI remains free to request arbitrary scientifically justified horizons and transformations.

Each derived feature definition must have a durable feature identifier, version, dependencies, required lookback, timing semantics, and predictor/outcome classification.

## 7. Feature-set versioning

The physical store uses immutable feature-set definitions. A feature set has a fixed column schema and versions of its member features.

Adding or materially changing a feature creates a new feature/version or feature-set version rather than silently rewriting historical scientific meaning.

This permits deterministic replay of findings produced under earlier definitions.

## 8. Incremental maintenance

The first historical build may acquire a large universe history once. Routine maintenance is incremental.

For each universe + feature set, Nexus records a last-complete effective session (high-water mark). A normal updater:

1. determines new completed sessions since the high-water mark;
2. acquires only the new source observations plus the maximum trailing lookback required by the selected features;
3. computes new point-in-time derived rows;
4. computes contemporaneous universe/sector ranks only after the eligible cross-section for that effective date is complete;
5. stages and validates the update;
6. atomically publishes the completed update;
7. advances the high-water mark;
8. releases disposable raw update cache data.

Weekly maintenance is an acceptable initial cadence. Daily maintenance can be added when Trading Engine requires it.

A failed update must not expose a partial market cross-section as current.

## 9. Historical immutability and corrections

Normal market progress appends new effective dates. It does not overwrite prior 252-session returns, ATR, ranks, or other historical point-in-time observations.

Source corrections, feature-definition defects, or identifier corrections require an explicit correction/rebuild path with version/provenance lineage. Silent historical mutation is prohibited.

## 10. Missingness and eligibility

Missing values require objective reason/status semantics where practical. IPOs, insufficient history, halts, unavailable shares outstanding, source failures, and true null measurements must not be treated as scientifically identical.

Each cross-sectional result must preserve the population definition and eligibility criteria used to form its denominator/sample.

## 11. Predictor/outcome separation and look-ahead

Forward outcomes may exist in the historical derived store for EXPLORATION and retrospective evaluation, but must be explicitly classified as outcomes/future-information.

Live or blind-prediction paths must mechanically prevent future-outcome columns from entering predictor inputs before the prediction point.

Point-in-time timing applies to earnings, shares outstanding, sector classification, index membership, and other fields that may be announced, revised, or effective at different times.

## 12. Cross-sectional statistical integrity

Large row counts must not be mistaken for independent observations. Analysis should support methods or robust summaries that account for:

- overlapping forward horizons;
- repeated observations from the same security;
- common market/regime shocks;
- temporal dependence;
- sector/common-factor structure;
- discovery-time threshold selection and multiple testing.

Temporal/regime/sector stability should be available as routine deterministic analysis capability without becoming a deterministic scientific decision-maker.

## 13. Campaign cache lifetime

During one AI research campaign, acquired raw source data should be reused across iterative Sol/Qwen cycles rather than repeatedly downloaded.

The cache may expand when AI asks a new scientifically valid question requiring more dates, fields, sources, or securities. It is eligible for cleanup only when the active research campaign no longer needs it.

Deterministic query-result caching may also reuse an exact previously executed analysis specification during the campaign.

## 14. Cross-sectional request execution

A universe/cohort request may reference Nexus-derived market data directly. The deterministic runtime materializes only the requested feature/date/security slice into campaign Analysis input.

AI receives compact outputs such as sample counts, universe coverage, effect sizes, distributions, temporal splits, sector/regime splits, robustness measures, limitations, and lineage. Raw universe rows are not placed in the AI prompt by default.

## 15. Runners and single-subject assumptions

Generic runners, validators, codecs, compilers, continuation logic, and Analysis lineage may retain backward-compatible `subject_id` fields, but must understand an explicit ResearchScope and must not require all evidence/result lineage to equal one ticker ID when the declared scope legitimately contains multiple subjects.

A scope itself has a durable `scope_id`. Cross-sectional results/findings may belong to a synthetic universe/cohort subject such as `universe:sp500:point_in_time` while retaining member-subject lineage.

## 16. Initial scientific acceptance controls

Before another expensive autonomous Sol discovery campaign, the assembled system must demonstrate that it can autonomously rediscover known relationships when supplied suitable data without being told the expected answer/direction:

1. cross-sectional momentum;
2. medium-term trend persistence;
3. short-horizon reversal;
4. post-earnings announcement drift;
5. at least one negative control.

PASS means the AI independently identifies approximately correct direction/horizon/conditioning and survives reasonable robustness checks. PARTIAL and FAIL must be recorded honestly.

A separate architecture control must prove that a universe-level request can be accepted, executed, compactly summarized, lineage-preserved, reused from cache where appropriate, and cleaned up only at terminal completion.

## 17. Sol-before-Qwen calibration gate

Qwen is not authorized to operate autonomously as the Research Director until Sol has established a documented historical benchmark and produced examples of successful and unsuccessful research approaches against the repaired system.

The intended sequence is:

1. deterministic backend and acceptance controls pass;
2. Sol runs the calibration/known-effect and selected historical research campaigns;
3. the resulting Research Packages, Analysis choices, promoted findings, rejected paths, continuation decisions, and negative examples are preserved as Qwen training/context material;
4. Qwen is brought online in supervised replay/shadow mode against those historical Sol traces;
5. Qwen must demonstrate contract competence and scientifically useful behavior before it is permitted autonomous research authority;
6. Sol remains available as the benchmark/appeal authority under the separately approved provider policy.

This is calibration and historical approach transfer, not hard-coding Sol's conclusions into Qwen or deterministic code.

## 18. Initial implementation boundary

The first backend implementation should provide:

- explicit ResearchScope contracts with single-subject backward compatibility;
- scope-aware validation/compiler behavior;
- a Nexus-owned Parquet derived market store with immutable feature-set/universe definitions, append-only incremental update batches, high-water marks, atomic manifest publication, and query slicing;
- feature lookback/update planning;
- runner/runtime access to the derived store;
- tests for scope acceptance, incremental append/high-water behavior, immutability, persistence/reload, and query slicing;
- no fabricated point-in-time S&P membership history and no credential-dependent live historical build until a server is available.

Live data acquisition, the initial full historical build, membership-source selection, empirical storage/performance tuning, and acceptance-control execution occur during integration testing on the next available server.
