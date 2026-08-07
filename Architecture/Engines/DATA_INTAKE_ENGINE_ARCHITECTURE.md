# Momentum Trading System v2 — Data-Intake Engine Architecture

**Status:** Draft for implementation

## 1. Mission

The Data-Intake Engine converts external observations into validated, normalized, objectively reproducible MTS data and deterministic measurements, then publishes governed artifacts through the Research Nexus.

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
- deterministic transformations;
- deterministic technical calculations;
- deterministic market-context comparisons;
- deterministic institutional-data measurements;
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
Baseline Measurement Plan
    ↓
Deterministic Measurement Modules
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

## 6. Hybrid Measurement Model

The Measurement Library may contain thousands of deterministic formulas. The engine must not materialize every possible measurement blindly.

### BASELINE
Automatically calculated when applicable source data is ingested.

A baseline measurement should generally be objective, widely reusable, reasonably economical, stable in definition, and supported by available inputs.

The baseline should be intentionally broad so downstream Analysis is not starved of factual context.

### ON_DEMAND
Known, governed, reproducible measurement calculated only when requested because it is specialized, expensive, unusually dependent, or narrowly applicable.

Once calculated, reusable output should be published so later research does not recompute it unnecessarily.

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

## 9. Measurement Module Architecture

Legacy "feature plugins" become v2 measurement modules.

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

## 10. Initial Baseline Measurement Families

For daily OHLCV, the first baseline should be generous.

### Source and identity
ticker/instrument identity, date/timestamp, source metadata, frequency, adjustment state, corporate-action fields when supplied, source-status fields.

### Price / return
raw OHLC, adjusted price where valid, typical price, simple returns, log returns, gaps, close/open relationships, distance and percent-distance measures.

### Candle geometry
range, body, upper/lower wick, close/open location, adjacent-bar overlap, inside/outside-bar geometry, higher/lower high/low facts.

These names describe geometry only; they carry no predictive meaning.

### Volume / liquidity
raw volume, dollar volume, rolling volume statistics, rolling dollar-volume statistics, relative volume, volume dispersion, turnover when inputs exist, objective liquidity proxies.

### Moving / smoothed measurements
SMA families, EMA families, distances from averages, slopes, and objective cross/ordering states.

A cross is a fact. "Bullish crossover" is interpretation and is prohibited.

### Volatility / range
true range, ATR families, realized volatility, range-normalized volatility, Parkinson, Garman-Klass, Rogers-Satchell, and Bollinger components as mathematical bands/distances.

### Momentum / oscillators
ROC, RSI, MACD components, PPO, stochastic values, Williams %R, CCI, MFI, TRIX, Aroon calculations.

No downstream implication is attached.

### Rolling structure
rolling high/low, distance from rolling high/low, range position, new-high/new-low facts, rolling drawdown, recovery distance, slope and dispersion measures.

### Context / relative market
when benchmark inputs exist: benchmark return, relative return, rolling correlation, relative volatility, ratios, and beta-like deterministic estimates under governed definitions.

### Data quality
missingness, duplicate status, monotonic timestamp status, invalid OHLC relationships, stale observations, gap counts, sample count, warmup availability, and source completeness.

## 11. Future Data Families

The same architecture extends to options, dark pools/blocks, fundamentals, insider activity, short interest, macro, and alternative data.

The rule remains: normalize observations, calculate reproducible measurements, make no inference about meaning.

## 12. Research-Request Interaction

```text
Research need
    ↓
Measurement requirement
    ↓
Does governed definition already exist?
    ├─ yes → calculate/retrieve as needed
    └─ no  → define + validate deterministic measurement
                ↓
            add to Measurement Library
                ↓
            calculate
                ↓
            publish reusable output
```

A research request does not make a measurement campaign-local by default.

Reusable objective measurements should become reusable MTS assets.

## 13. Implementation Conformance

The Data-Intake Engine is not conformant until tests prove:

1. arbitrary supported external formats enter through adapters;
2. malformed input fails before publication;
3. normalization is deterministic;
4. baseline measurements reproduce exactly from the same inputs/version;
5. on-demand measurements can be requested independently;
6. reuse prevents unnecessary recomputation;
7. OBSERVED and DERIVED provenance remain distinguishable;
8. CONTEMPORANEOUS and RETROSPECTIVE measurements cannot be confused;
9. interpretation is absent from Data-Intake outputs;
10. canonical tabular artifacts publish through the Research Nexus;
11. Nexus retrieval reproduces the published dataset;
12. integrity verification succeeds;
13. transient input is removed only after verified publication;
14. failed publication preserves transient input for retry;
15. identical intake is idempotent;
16. no durable state is written directly outside Nexus;
17. no hard-coded repository path is required;
18. baseline calculation is batched/vectorized sufficiently for scale;
19. EXTERNAL_DATA_REQUIRED definitions remain registered without invented values;
20. adding a source adapter does not change the public Data-Intake contract.

## 13A. Shared Deterministic Computation and Calibration

The governed deterministic computation capability is a shared system resource rather than an Engine-specific limitation.

- Data Intake may materialize a broad governed set of deterministic measurements as part of canonical dataset construction.
- Analysis may invoke the same governed deterministic computations when an RP requires a measurement that was not materialized by Intake, requires different parameters, or requires recomputation against another valid dataset.
- Analysis is never limited to the measurements already attached by Intake.
- Deterministic computation remains separate from analytical interpretation. Comparative inference, predictive validation, incremental contribution, robustness, interaction analysis, economic significance, contradiction testing, generalization, and similar research procedures remain Analysis responsibilities.
- Controlled calibration campaigns may intentionally materialize the complete applicable governed deterministic computation set. This does not permanently define the production Intake baseline.
- Research evidence may change which deterministic measurements Intake routinely materializes, while lower-ranked measurements remain available in the shared governed computation library.

The permanent architecture therefore separates **availability of deterministic computation** from **routine Intake materialization**.

## 14. First Vertical Slice

```text
Fresh external daily-price CSV
    ↓
generic CSV adapter
    ↓
canonical OHLCV observations
    ↓
initial broad baseline measurement families
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

The Data-Intake Engine is deliberately data-rich and interpretation-free.

Its deterministic measurement capability is drawn from the shared governed computation library. Intake may materialize a broad baseline for reuse and efficiency, while Analysis retains access to the full governed library and is not constrained by the measurements Intake materialized.

Its permanent design centers on:
- broad objective measurement;
- reproducibility;
- versioned definitions;
- a reusable governed Measurement Library;
- source/format-independent adapters;
- measurement modules;
- rich baseline measurements plus an on-demand long tail;
- explicit temporal availability;
- Research Nexus publication and reuse.

Legacy migration decisions belong in the separate migration record and are not part of this engine's permanent identity.
