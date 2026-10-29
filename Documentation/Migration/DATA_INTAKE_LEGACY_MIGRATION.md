# Momentum Trading System v2 — Data-Intake Legacy Migration

**Status:** Active migration/audit record  
**Purpose:** Compare legacy Engine 08 capabilities with the canonical v2 Data-Intake Engine architecture. This document is transitional and is not part of the permanent engine identity.

## 13. Legacy Engine 08 Migration Matrix

### KEEP conceptually
- objective-measurement philosophy;
- Measurement Library;
- versioned formulas;
- measurement registry;
- module execution registry;
- runtime measurement audit;
- reproducibility requirements;
- explicit missing/unavailable state;
- candle geometry;
- price/return measurements;
- moving averages;
- volatility;
- momentum mathematics;
- volume/liquidity;
- benchmark/relative calculations;
- deterministic signal-processing transforms;
- data-quality measurements.

### REDESIGN
- "feature" terminology → "measurement" at the Data-Intake boundary;
- feature plugins → measurement modules;
- feature registry → governed Measurement Registry;
- source-specific loader assumptions → adapters;
- local manifests → Nexus provenance/publication;
- legacy Warehouse writers → Research Nexus publication;
- proposal-specific permanent outputs → reusable artifacts;
- column-by-column DataFrame mutation → batched/vectorized family generation;
- repository-path dependencies → governed configuration and Nexus references.

### MOVE DOWNSTREAM
- feature importance;
- usefulness;
- redundancy classification;
- predictive contribution;
- statistical significance;
- event recognition;
- clustering;
- interpretation;
- hypothesis generation;
- institutional-intent inference;
- opportunity scoring;
- recommendations;
- trade decisions.

### MOVE TO RESEARCH DIRECTOR / TASK MANAGEMENT
- Research Proposal creation;
- research-question ownership;
- research-priority selection;
- workflow scheduling;
- retry/routing policy.

### DELETE / RETIRE
- legacy filesystem coupling;
- legacy Warehouse mutation paths;
- duplicated local caches where Nexus reuse is available;
- numeric engine identity as architectural identity;
- campaign-local copies of reusable objective measurements;
- compatibility scaffolding not required by v2.

### MISSING IN LEGACY / REQUIRED IN V2
- source-agnostic adapter contract;
- canonical transient-input lifecycle;
- publish-then-verify-before-delete;
- OBSERVED vs DERIVED provenance;
- BASELINE vs ON_DEMAND calculation policy;
- CONTEMPORANEOUS vs RETROSPECTIVE temporal scope;
- governed Measurement Registry;
- Nexus-native artifact references;
- measurement reuse before recomputation;
- explicit external-data availability state;
- functional identity: Data-Intake Engine.

## 14. Legacy Family Disposition

| Legacy family | v2 disposition |
|---|---|
| CANDLE_GEOMETRY | Baseline candidate |
| PRICE_RETURN | Baseline candidate |
| TREND | Baseline candidate after terminology audit |
| MOMENTUM | Baseline candidate |
| VOLATILITY | Baseline candidate |
| VOLUME_LIQUIDITY | Baseline candidate |
| MARKET_STRUCTURE | Field-by-field objectivity audit |
| ADVANCED_MARKET_STRUCTURE | Field-by-field objectivity audit; many likely on-demand |
| CONTEXT_COMPARISON | Baseline where benchmark data is routine; otherwise on-demand |
| DATA_QUALITY | Baseline |
| RELATIVE_MARKET | Baseline/on-demand depending on dependency |
| SIGNAL_PROCESSING | Mostly on-demand initially; deterministic formulas allowed |
| INFORMATION_COMPLEXITY | On-demand initially; formula-level audit |
| EVENT_GEOMETRY | Redesign terminology/use; retrospective or request-scoped unless a non-interpretive interval is explicitly supplied |
| EXTERNAL_DATA | Keep definitions; mark EXTERNAL_DATA_REQUIRED until inputs exist |

## 15. Key Architectural Correction from Legacy

Legacy execution was heavily request-driven. That minimized up-front computation but could starve Analysis of objective facts and force repeated recursive Research Proposals.

v2 uses:

```text
External Data
    ↓
Rich Baseline Measurements
    ↓
Research Nexus
    ↓
Analysis has substantial factual context
    ↓
Only genuinely specialized missing measurement
    ↓
On-demand Data-Intake task
    ↓
Reusable measurement published
```

The goal is not to eliminate on-demand requests. The goal is to ensure Research Proposals are generated because research discovered a genuinely new information requirement, not because Data Intake withheld cheap, broadly useful objective facts.
