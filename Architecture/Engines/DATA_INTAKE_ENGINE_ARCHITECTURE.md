# Momentum Trading System v2 — Data-Intake Engine Architecture and Legacy Comparison

**Status:** Draft for implementation

## 1. Mission

The Data-Intake Engine converts external observations into validated, normalized, objectively reproducible MTS data, applies only a deliberately small governed baseline of routine measurements, and publishes governed artifacts through the Research Nexus.

It must never assign meaning, significance, predictive value, importance, trading implication, or scientific authority to the measurements it produces.

> Every knowledgeable practitioner should be able to agree on the recorded value when given the same source observations, governed definition, parameters, and formula version.

If a result requires interpretation, judgment, classification of significance, prediction, causal explanation, or trading inference, it belongs downstream.

## 2. Responsibility Boundary

Data Intake owns:
- external-source ingestion;
- source adapters;
- file/stream format handling;
- source-field mapping;
- structural validation;
- normalization;
- canonical identifiers, timestamps, and units;
- objective data-quality measurements;
- execution of the governed Intake-baseline measurement subset;
- reuse of governed Tool Library measurement definitions when assigned to Intake;
- canonical tabular representation;
- measurement-definition execution;
- publication requests to the Research Nexus;
- verification before transient-input cleanup.

Data Intake does not own:
- hypotheses;
- research-question generation;
- predictive analysis;
- statistical significance;
- feature importance;
- redundancy judgments;
- event recognition;
- event-family discovery;
- causal interpretation;
- bullish/bearish labels;
- institutional-intent inference;
- opportunity scoring;
- trade decisions;
- knowledge promotion.

## 3. Canonical Flow

```text
External Data
    ↓
Source Adapter
    ↓
Canonical Observation Model
    ↓
Structural / Data-Quality Validation
    ↓
Normalization
    ↓
Minimal Intake Baseline Plan
    ↓
Governed Baseline Measurement Modules
    ↓
Canonical Dataset Representation
    ↓
Research Nexus Publication
    ↓
Integrity Verification
    ↓
Transient Source Cleanup
```

A transient input file is deleted only after the canonical artifact is successfully published and verified.

## 4. Source and Format Independence

The engine is not Yahoo-specific and not CSV-specific.

Adapters translate external contracts into canonical observation models.

Examples:
- CSVAdapter
- ParquetAdapter
- JSONAdapter
- REST/APIAdapter
- StreamingAdapter
- OptionsVendorAdapter
- DarkPoolAdapter
- FundamentalDataAdapter
- InsiderDataAdapter
- ShortInterestAdapter
- MacroDataAdapter

Adapters must not contain hidden analytical policy.

## 5. Observation vs Measurement

### OBSERVED
A value supplied directly by a source after canonical normalization.

Examples:
- open
- high
- low
- close
- volume
- option_contract_volume
- open_interest
- strike
- expiration
- trade_price
- trade_size
- dark_pool_venue
- earnings_per_share
- shares_outstanding

### DERIVED
A deterministic calculation from governed inputs.

Examples:
- return_1d
- log_return_1d
- dollar_volume
- relative_volume_20
- sma_20
- ema_20
- atr_14
- rsi_14
- macd_line
- realized_vol_20
- distance_from_high_20
- option_volume_oi_ratio
- days_to_expiration
- option_notional
- dark_pool_notional

Both OBSERVED and DERIVED values are data. Their provenance must distinguish them.

## 6. Shared Tool Library and Intake Materialization Policy

MTS maintains a shared governed Tool Library containing reusable measurement definitions and analytical capabilities. The Data-Intake Engine does not own the full Tool Library and must not materialize every available measurement by default.

The absence of a measurement from Intake output must never imply that the measurement is unavailable to downstream Analysis. Analysis may retrieve canonical observations from the Research Nexus and invoke any governed Tool Library capability permitted by its contract.

### INTAKE_BASELINE
Automatically calculated by Data Intake when applicable source data is ingested.

The initial Intake baseline should be deliberately small. A baseline measurement should generally be:
- universally or near-universally reusable;
- inexpensive to calculate and store;
- stable in definition;
- supported by routinely available inputs; and
- operationally valuable enough to justify materialization on substantially every compatible ticker.

Baseline membership is an operational materialization decision, not a scientific-value judgment.

### ANALYSIS_ON_DEMAND
A governed measurement or analytical capability available to Analysis without requiring prior Intake materialization. Analysis may calculate these from canonical Nexus data when needed to execute a Research Proposal or standard analysis contract.

Analysis is not constrained by the Intake baseline. It may also create candidate deterministic tools when existing governed tools are insufficient, subject to validation and governance before broad reuse.

### EVIDENCE-DRIVEN PROMOTION / DEMOTION
Tool use, contribution, redundancy, applicability, computational cost, and repeated research value are tracked downstream. Research Cache evidence may support recommending that a reusable measurement be promoted into the Intake baseline.

A measurement may later be demoted from Intake materialization if routine computation is no longer justified. Demotion removes automatic materialization only; it does not delete the governed tool from the shared Tool Library.

### EXTERNAL_DATA_REQUIRED
A defined measurement that cannot currently be produced because required external observations are unavailable.

This is an availability state, not a scientific judgment.

## 7. Temporal Scope

Calculation policy and temporal availability are independent.

### CONTEMPORANEOUS
Uses only information available at or before the observation timestamp.

Examples:
- ema_20
- relative_volume_20
- atr_14
- rsi_14
- rolling_high_20

### RETROSPECTIVE
Objectively computed using later observations.

Examples:
- forward_return_5d
- maximum_favorable_excursion_20d
- maximum_adverse_excursion_20d
- days_to_future_peak
- future_path_range

Retrospective measurements are legitimate historical data but must be explicitly tagged so they cannot leak into decision-time inputs.

## 8. Measurement Definition Contract

Every governed measurement definition should carry at least:

```text
measurement_id
name
family
definition
observation_or_derived
required_inputs
parameters
units
output_type
formula_version
implementation_version
calculation_policy
temporal_scope
data_family
minimum_history
availability
computational_cost
validation_status
dependency_measurements
```

Optional but useful:
- precision
- null_semantics
- warmup_behavior
- expected_range
- source_constraints
- applicable_asset_types
- applicable_frequencies
- deprecation_state
- replacement_measurement_id

## 9. Tool and Measurement Module Architecture

Legacy "feature plugins" become governed Tool Library modules. Measurement modules may be executed by Data Intake when assigned to the Intake baseline or by Analysis when requested on demand. Engine ownership must not be encoded into the mathematical definition itself.

Each module declares:
- module_id
- family
- version
- input_requirements
- measurement_ids
- dependencies
- deterministic_behavior
- estimated_cost

Execution produces a runtime audit with:
- module_id
- module_version
- input_columns
- measurements_requested
- measurements_reused
- measurements_computed
- elapsed_time
- status
- errors
- output_artifact_refs

The engine should calculate families in batches rather than repeatedly inserting one column at a time.

## 10. Initial Intake Baseline

For daily OHLCV, the first Intake baseline should be deliberately minimal and sufficient to establish a trustworthy canonical record.

### Required canonical observations and identity
ticker/instrument identity, date/timestamp, raw OHLCV, source metadata, frequency, adjustment state, corporate-action fields when supplied, and source-status fields.

### Required data-quality facts
missingness, duplicate status, timestamp-order validation, invalid OHLC relationships, source completeness, and other inexpensive integrity facts required to certify the canonical dataset.

### Small universal derived baseline
Only a limited set of cheap, broadly reusable derived measurements should be materialized initially. Exact membership is governed separately from this architecture and may include measurements such as simple return, log return, dollar volume, true range/ATR normalization, or other primitives demonstrated to justify universal materialization.

ATR or comparable volatility normalization may be included where required by the standard downstream characterization contract, but Intake must not become responsible for opportunity recognition or research interpretation.

### Not automatically materialized
Moving-average families, oscillators, advanced volatility estimators, market-structure calculations, signal-processing transforms, retrospective outcome geometry, and other specialized measurements remain available through the shared Tool Library unless separately promoted into the Intake baseline.

The legacy Engine 08 measurement registry is therefore treated as a Tool Library seed inventory, not as a mandate to attach every legacy measurement to every ticker.

## 11. Future Data Families

The same architecture extends to options, dark pools/blocks, fundamentals, insider activity, short interest, macro, and alternative data.

The rule remains: normalize observations, calculate reproducible measurements, make no inference about meaning.

## 12. Research-Request and Analysis Interaction

```text
Research need / standard Analysis task
    ↓
Required measurement or analytical capability
    ↓
Does governed Tool Library capability already exist?
    ├─ yes → Analysis retrieves/reuses or calculates from canonical Nexus data
    └─ no  → Analysis may create a candidate tool
                ↓
            validate + govern reusable definition
                ↓
            add to shared Tool Library when approved
                ↓
            execute
                ↓
            publish exploratory output to Research Cache
```

Data Intake is not the gatekeeper of Analysis capability. A research request does not require the needed measurement to have been materialized at intake.

Exploratory Analysis outputs belong first in the governed Research Cache. Durable attachment or promotion is a separate lifecycle decision. Frequently useful and demonstrably valuable measurement tools may later be recommended for Intake-baseline promotion.

## 13. Implementation Conformance

The Data-Intake Engine is not conformant until tests prove:

1. arbitrary supported external formats enter through adapters;
2. malformed input fails before publication;
3. normalization is deterministic;
4. Intake-baseline measurements reproduce exactly from the same inputs/version;
5. Analysis capability is not constrained by Intake-baseline membership;
6. governed Tool Library measurements can be calculated downstream from canonical Nexus data without engine-to-engine bypass;
7. reuse prevents unnecessary recomputation;
8. OBSERVED and DERIVED provenance remain distinguishable;
9. CONTEMPORANEOUS and RETROSPECTIVE measurements cannot be confused;
10. interpretation is absent from Data-Intake outputs;
11. canonical tabular artifacts publish through the Research Nexus;
12. Nexus retrieval reproduces the published dataset;
13. integrity verification succeeds;
14. transient input is removed only after verified publication;
15. failed publication preserves transient input for retry;
16. identical intake is idempotent;
17. no durable state is written directly outside Nexus;
18. no hard-coded repository path is required;
19. baseline calculation is batched/vectorized sufficiently for scale;
20. EXTERNAL_DATA_REQUIRED definitions remain registered without invented values;
21. adding a source adapter does not change the public Data-Intake contract.


## 14. First Vertical Slice

```text
Fresh external daily-price CSV
    ↓
generic CSV adapter
    ↓
canonical OHLCV observations
    ↓
minimal governed Intake baseline
    ↓
canonical Parquet
    ↓
Research Nexus publish
    ↓
retrieve + verify
    ↓
delete transient CSV
```

AAPL is a useful first fixture, but no Yahoo- or AAPL-specific assumption belongs in the engine architecture.

## 15. Architectural Decision

The Data-Intake Engine is deliberately lean, deterministic, and interpretation-free.

Its permanent design centers on:
- trustworthy acquisition and normalization of external observations;
- a deliberately small, governed Intake baseline;
- reproducibility and versioned definitions;
- a shared governed Tool Library that is not owned or limited by Intake;
- source/format-independent adapters;
- reusable measurement modules executable by authorized engines;
- downstream Analysis freedom beyond the Intake baseline;
- evidence-driven promotion and demotion of routine materialization;
- explicit temporal availability;
- Research Nexus publication, retrieval, and reuse;
- no direct engine-to-engine data bypass.

Legacy migration decisions belong in the separate migration record and are not part of this engine's permanent identity.
