# Momentum Trading System — Data Quality Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, `ARTIFACT_GOVERNANCE_STANDARD.md`, `SCHEMA_STANDARD.md`, `STORAGE_RETENTION_STANDARD.md`, `ENGINE_INTERFACE_STANDARD.md`, and `TASK_MANAGEMENT_STANDARD.md`.

---

## 1. Purpose

This standard defines how Momentum Trading System (MTS) determines whether data is sufficiently complete, coherent, temporally valid, traceable, and fit for a declared use.

It governs quality evaluation for:

- raw market data;
- normalized datasets;
- derived datasets;
- feature data;
- institutional/activity data;
- fundamental/context data;
- live-market data;
- instrument/reference data;
- future data families.

Data quality is a prerequisite to valid research and decision-making.

---

## 2. Governing Principle

> **MTS must know what data it has, what it does not have, when it became knowable, what transformations occurred, and whether it is fit for the specific use being attempted.**

“Loaded successfully” is not a data-quality result.

---

## 3. Quality Is Fitness for Use

Quality is not one universal binary property.

A dataset may be acceptable for:

- exploratory historical research;

but unacceptable for:

- event-time sequencing;
- intraday execution analysis;
- live Decision input.

Quality evaluation must therefore identify the intended use or quality profile.

---

## 4. No Silent Repair

MTS must not silently repair, fabricate, interpolate, forward-fill, drop, or substitute scientifically material data.

Any correction or transformation that can affect interpretation must be:

- governed;
- reproducible;
- recorded;
- attributable;
- distinguishable from raw source data.

---

## 5. Raw Source Fidelity

Canonical raw source artifacts preserve what the provider/source delivered.

Raw source data should not be mutated to make it “clean.”

Corrections create a new normalized/corrected artifact with provenance back to the source.

---

## 6. Quality Dimensions

Quality evaluation should consider, as applicable:

```text
schema validity
completeness
temporal integrity
uniqueness
consistency
range/plausibility
cross-field coherence
continuity
source fidelity
instrument identity
corporate-action integrity
unit integrity
freshness
provenance completeness
availability-time integrity
```

Additional domain-specific dimensions may be governed later.

---

## 7. Quality Result

A quality evaluation must produce a machine-readable result.

Conceptually:

```text
PASS
PASS_WITH_WARNINGS
FAIL
NOT_EVALUATED
NOT_APPLICABLE
```

Exact vocabulary belongs in Governance/Schemas.

Warnings must remain visible to downstream consumers.

---

## 8. Quality Profile

The applicable checks should be defined by a governed quality profile.

Examples:

```text
HISTORICAL_DAILY_OHLCV
HISTORICAL_INTRADAY
LIVE_MARKET
OPTIONS_ACTIVITY
FUNDAMENTAL_POINT_IN_TIME
INSTRUMENT_REFERENCE
```

A profile defines required checks and thresholds for that use.

---

## 9. Objective Criteria

Quality gates must use objective criteria where possible.

Examples:

- required columns present;
- duplicate-key count = 0;
- timestamps monotonic within defined grouping;
- missing-session rate below governed threshold;
- OHLC relationships valid;
- volume nonnegative;
- source identity present;
- availability timestamps present where required.

Undefined “looks clean” judgments are not sufficient.

---

## 10. Schema Validation

Data must conform to its declared schema before quality acceptance.

Schema validity alone does not prove data quality.

A structurally valid dataset can still contain scientifically invalid values.

---

## 11. Required Field Completeness

Quality evaluation must identify missing required fields.

Missingness must distinguish, where possible:

```text
not provided by source
not applicable
not measured
unknown
corrupted
missing record
```

Missing values must not silently become zero.

---

## 12. Record Completeness

For time-series data, MTS must evaluate expected record coverage appropriate to the source and market calendar.

Missing dates/bars may be legitimate due to:

- weekends;
- holidays;
- halts;
- listing dates;
- delisting;
- provider coverage limits.

Quality logic must not manufacture records simply to make a series continuous.

---

## 13. Duplicate Records

Duplicate logical records must be detected using governed keys.

A duplicate must not be removed silently when differing values exist.

Conflicting duplicates require explicit resolution or failure.

---

## 14. Temporal Ordering

Time-series data must be checked for appropriate ordering and duplicate timestamps.

Ordering assumptions must be defined by schema/profile.

---

## 15. Observation vs Availability Time

Where relevant, MTS must validate both:

```text
observed_at
available_at
```

Historical research must not consume data before it would have been available.

This is a core defense against look-ahead bias.

---

## 16. Time Zones

Timestamps must have governed timezone/session semantics.

MTS must not infer timezone from the developer's local machine.

Conversion between provider time and canonical time must be explicit and reproducible.

---

## 17. Market Sessions

Market data quality should recognize:

- regular sessions;
- extended hours where supported;
- market holidays;
- early closes;
- halts;
- special sessions.

Session rules should come from governed market-calendar logic rather than hard-coded assumptions scattered across engines.

---

## 18. OHLC Coherence

For conventional OHLC bars, checks should include relationships such as:

```text
high >= open
high >= close
low <= open
low <= close
high >= low
```

Invalid bars must be flagged.

Whether correction is possible depends on source and policy.

---

## 19. Price Plausibility

Price fields should be checked for impossible or suspicious values appropriate to instrument type.

Examples:

- nonpositive conventional equity price;
- extreme discontinuity;
- decimal/scale error;
- split-like discontinuity without corresponding corporate-action context.

Suspicious does not automatically mean wrong.

An anomaly may be real market information.

---

## 20. Volume Integrity

Volume checks should consider:

- nonnegative values;
- source definition;
- units;
- missingness;
- extreme anomalies;
- whether the provider reports true share volume or another measure.

MTS must not label dollar volume as share volume or vice versa.

---

## 21. Dollar Volume

When average dollar volume is computed, its definition must be explicit.

For example, a governed calculation may use:

```text
price measure × share volume
```

The exact price measure and aggregation window must be declared.

Downstream engines must not infer the definition from a field name.

---

## 22. Adjusted vs Unadjusted Prices

Datasets must identify whether prices and volumes are:

```text
raw/unadjusted
split-adjusted
dividend-adjusted
total-return adjusted
other governed adjustment
```

MTS must not mix adjusted and unadjusted fields without explicit transformation semantics.

---

## 23. Corporate Actions

Historical equity data quality must account for corporate actions where relevant.

Examples:

- splits;
- reverse splits;
- dividends;
- mergers;
- spin-offs;
- symbol changes.

Corporate-action processing must preserve point-in-time integrity.

---

## 24. Instrument Identity

Quality evaluation must confirm that records map to the intended governed instrument identity.

Ticker symbol alone is insufficient for permanent identity.

Symbol reuse or symbol changes must not silently merge different instruments.

---

## 25. Listing Coverage

Dataset coverage should identify:

```text
first_available_observation
last_available_observation
expected coverage
actual coverage
known source limitations
```

A ten-year request satisfied by three years of provider history must not silently pass as complete.

---

## 26. Source Provenance

Every admitted source dataset must identify its source sufficiently to reproduce or audit acquisition.

Where applicable:

```text
provider
dataset/product
request/acquisition parameters
acquired_at
source version
license context
source artifact identity
```

---

## 27. Source Changes

If a provider changes:

- schema;
- historical values;
- adjustment methodology;
- coverage;
- definitions;

MTS must detect or record the change where feasible.

A provider revision must not silently rewrite prior canonical raw artifacts.

---

## 28. Cross-Source Comparison

Cross-source comparison may be used to identify anomalies.

Disagreement between sources is evidence requiring investigation, not automatic proof that one source is wrong.

The source selected as canonical for a given purpose must be governed.

---

## 29. Derived Data Quality

Derived datasets inherit quality dependencies from their inputs.

A derived artifact must not receive a stronger quality claim than its inputs justify without explicit methodology.

Its quality record should reference:

- source quality results;
- transformation validation;
- derived-specific checks.

---

## 30. Feature Quality

Computed features must define:

- formula/version;
- required lookback;
- warm-up behavior;
- missing-input behavior;
- units/scaling;
- availability timing.

Feature values produced before sufficient lookback must not silently appear valid.

---

## 31. Rolling Calculations

Rolling features must specify:

- window length;
- minimum observations;
- alignment;
- inclusion/exclusion of current bar;
- treatment of missing observations.

These choices materially affect historical research.

---

## 32. Normalization Quality

Normalization must preserve semantic equivalence to source data except for explicitly documented transformations.

Quality checks should verify:

- record counts;
- key coverage;
- unit conversion;
- timestamp conversion;
- mapping completeness;
- value preservation where expected.

---

## 33. Outliers

Outliers must not be removed solely because they are statistically unusual.

In markets, extreme observations may be the most important events.

Outlier handling must distinguish:

```text
suspected data error
legitimate extreme market event
unknown
```

---

## 34. Anomaly Quarantine

Suspected corrupt data may be quarantined from ordinary downstream use without deleting the source artifact.

Quarantine must preserve:

- identity;
- reason;
- quality evidence;
- remediation status.

---

## 35. Quality Failure

A dataset that fails a required quality gate must not be published as accepted input for that governed use.

It may still be preserved as:

- raw source;
- quarantined artifact;
- diagnostic evidence.

Failure must be explicit.

---

## 36. Warning

A warning indicates a known limitation that does not necessarily block use.

Warnings must be machine-readable and discoverable by downstream engines.

A consumer may impose stricter requirements than the producer.

---

## 37. Quality Promotion

Data may become eligible for a broader use only after satisfying the applicable quality profile.

Example:

```text
raw acquired
→ schema valid
→ normalized
→ quality validated
→ accepted for historical daily research
```

Acceptance for one use does not imply acceptance for all uses.

---

## 38. Live Data Freshness

Live-market quality must include freshness.

A live datum should support metadata such as:

```text
observed_at
received_at
age
source
```

A stale datum must not silently be treated as current.

---

## 39. Live Feed Gaps

Live systems must detect feed gaps or stalled streams.

A connected socket or running process is not proof that current market data is arriving.

---

## 40. Live vs Historical Reconciliation

Where live observations later become historical records, MTS may reconcile them.

Reconciliation must not rewrite what was actually known to the Decision Engine at decision time.

---

## 41. Institutional / Alternative Data

Institutional or alternative datasets require source-specific quality definitions.

Examples may include:

- dark-pool data;
- block trades;
- options sweeps;
- insider activity;
- options open interest.

MTS must preserve the provider's actual definitions and limitations rather than converting marketing labels into assumed facts.

---

## 42. Options Data

Options-related quality may require validation of:

- underlying instrument;
- expiration;
- strike;
- option type;
- trade/quote timestamp;
- contract multiplier;
- bid/ask context;
- volume;
- open interest;
- source methodology.

Claims such as “sweep” must preserve the provider/algorithm definition used to classify the event.

---

## 43. Fundamental Data

Fundamental data must preserve point-in-time availability where used in historical research.

Restated financials must not be substituted for originally available values without explicit methodology.

---

## 44. Reference Data

Reference data quality includes:

- symbol-to-instrument mapping;
- exchange;
- asset type;
- effective dates;
- corporate-action continuity.

Reference-data errors can contaminate otherwise valid price data.

---

## 45. Survivorship Bias

Research universes must preserve historical membership where required.

Using today's surviving securities as the historical universe can introduce survivorship bias.

Quality evaluation must identify whether the universe is point-in-time valid.

---

## 46. Selection Bias Metadata

Where data collection itself is filtered, the filtering/selection process must be preserved.

MTS must know whether a dataset represents:

- complete universe;
- screened subset;
- event-selected sample;
- convenience sample.

---

## 47. Look-Ahead Contamination

Quality validation for research must test against future information leakage.

Potential sources include:

- future-adjusted labels;
- later fundamentals;
- revised provider data;
- outcome-derived feature construction;
- future universe membership;
- overlapping target windows.

---

## 48. Overlapping Events / Samples

Where research methodology excludes overlapping opportunities or samples, the rule must be explicit and testable.

Overlap handling belongs to the relevant research/data contract and must be reflected in derived dataset provenance.

---

## 49. Data Leakage Across Training and Evaluation

Datasets used for learning, discovery, validation, and holdout evaluation must preserve partition boundaries.

No engine may silently contaminate holdout data with training information.

---

## 50. Quality Metrics

Quality reports should include quantitative metrics where useful.

Examples:

```text
row_count
duplicate_count
missing_count
missing_rate
coverage_rate
invalid_bar_count
timestamp_gap_count
mapping_failure_count
warning_count
```

Metrics supplement, not replace, the final quality result.

---

## 51. Quality Artifact

Material quality evaluation should itself be a governed artifact or governed metadata record.

It should identify:

```text
dataset_ref
quality_profile
profile_version
check_results
metrics
warnings
result
evaluated_at
execution_ref
```

---

## 52. Revalidation

Quality may require revalidation when:

- source is revised;
- schema changes;
- quality profile changes;
- corruption is detected;
- new downstream use imposes stronger requirements.

Prior quality history remains preserved.

---

## 53. Data Corruption

Integrity/hash failure is distinct from scientific quality failure.

Corrupted storage must trigger storage recovery/invalidation procedures.

A scientifically implausible but byte-intact observation requires data-quality investigation.

---

## 54. Intake Responsibility

Data Intake is responsible for applying or invoking required intake quality checks before publication into accepted downstream state.

It must not make research conclusions from those checks.

---

## 55. Downstream Responsibility

Downstream engines must verify that input artifacts satisfy the quality profile required for their use.

They must not assume that existence in the Nexus means universally fit.

---

## 56. No Private Quality Rules

Material data-quality rules must not exist only as hidden engine code.

They must be represented in governed profiles, contracts, schemas, policies, or shared quality libraries as appropriate.

---

## 57. Quality Rule Versioning

Quality profiles and rules must be versioned.

Historical research should be able to identify which quality rules were applied.

A stricter future rule does not silently rewrite past evaluation history.

---

## 58. Quality and Deletion

Failed or quarantined raw evidence must not automatically be deleted.

It may be required to:

- diagnose provider problems;
- reproduce a failure;
- explain exclusion;
- compare corrected versions.

Retention follows `STORAGE_RETENTION_STANDARD.md`.

---

## 59. Quality and SoK

The State of Knowledge should consume only artifacts whose data-quality standing satisfies the relevant scientific use.

Quality limitations should propagate into uncertainty and applicability rather than disappear during interpretation.

---

## 60. Quality and Decision

Decision must not consume data that fails its required quality/freshness profile.

If required current data is unavailable or stale, the correct semantic result may be:

```text
NO_ACTION
MISSING_CAPABILITY
INSUFFICIENT_CURRENT_DATA
```

according to the Decision contract.

It must not fabricate missing state.

---

## 61. Initial v2 Implementation

The first Data Quality implementation should support at least:

1. schema validation;
2. required-field checks;
3. duplicate detection;
4. timestamp/order checks;
5. daily OHLC coherence;
6. nonnegative volume;
7. instrument identity mapping;
8. coverage reporting;
9. adjusted/unadjusted metadata;
10. provenance completeness;
11. machine-readable quality results;
12. quarantine on required-check failure.

This is sufficient to begin historical daily research without pretending the full future data universe already exists.

---

## 62. Testing Requirements

Tests must include:

- valid dataset pass;
- missing required field;
- duplicate record;
- conflicting duplicate;
- invalid OHLC;
- negative volume;
- missing session;
- legitimate holiday;
- timezone conversion;
- symbol change;
- insufficient history;
- look-ahead availability violation;
- split/corporate-action case;
- quarantined failure;
- warning-only result;
- deterministic quality metrics.

---

## 63. Conformance

A component conforms when it:

1. preserves raw source fidelity;
2. does not silently repair material data;
3. uses governed quality profiles;
4. validates schema and semantic quality separately;
5. preserves temporal/availability integrity;
6. detects duplicates and conflicting records;
7. defines units and adjustment semantics;
8. preserves instrument identity;
9. records coverage and provenance;
10. treats outliers as evidence until investigated;
11. produces machine-readable quality results;
12. blocks downstream use when required gates fail;
13. propagates warnings/limitations;
14. supports revalidation without rewriting history.

---

## 64. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/RESEARCH_STANDARD.md
Governance/Standards/DECISION_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 65. Closing Principle

MTS must always be able to answer:

> **What exactly was collected, what is missing, what transformations occurred, when was each fact actually knowable, and is this data fit for the specific scientific or decision use being attempted?**

If MTS cannot answer those questions, the data is not ready to support a governed conclusion.
