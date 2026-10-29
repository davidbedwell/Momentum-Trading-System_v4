# Momentum Trading System — Analysis Engine Technical Design

**Status:** Proposed\
**Authority:** Technical implementation design subordinate to
`CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`,
`Architecture/ENGINE_ARCHITECTURE.md`,
`Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`,
`Architecture/Engines/ANALYSIS_ENGINE_ARCHITECTURE.md`, and governing
Research/Data/Artifact standards and contracts\
**Component:** Analysis Engine\
**Governance Role:** Historical/scientific empirical analysis\
**Design Principle:** Bounded scientific execution behind governed task
and Research Nexus contracts\
**Legacy Policy:** Clean v2 implementation. Legacy Engine 09 may inform
lessons only and is not a software, schema, import, storage,
orchestration, or directory dependency.

------------------------------------------------------------------------

## 1. Purpose

This document translates the Analysis Engine architecture into an
implementable v2 technical design.

The Analysis Engine shall execute admitted, bounded empirical work
against governed Research Nexus inputs and publish durable scientific
evidence and Findings back through Research Nexus.

The implementation must make the following path real:

``` text
governed Analysis task
    ↓
resolve Research Nexus inputs
    ↓
construct Scientific Execution Context
    ↓
validate authority + compatibility
    ↓
construct reproducible sample
    ↓
materialize additional governed deterministic computations if required
    ↓
execute approved Analysis method(s)
    ↓
validate analytical output
    ↓
retain transient intermediates in Research Cache
    ↓
construct canonical evidence / Finding artifacts
    ↓
publish through Research Nexus
    ↓
retrieve + verify + reconcile retry
    ↓
return bounded Task Result
```

The engine is analytically extensible but authority-limited.

It does not own research intent, Research Admission, global scheduling,
external acquisition, durable enterprise storage, knowledge promotion,
investment decisions, or trade execution.

------------------------------------------------------------------------

## 2. Design Goals

The first implementation shall satisfy these goals:

1.  **Nexus-only durable boundary** --- durable inputs are resolved from
    Research Nexus and durable outputs are published through Research
    Nexus.
2.  **Task-bounded execution** --- Analysis performs only work
    authorized by a governed task and its referenced Research
    Plan/question.
3.  **Scientific reproducibility** --- material results preserve enough
    context to reconstruct inputs, samples, methods, parameters,
    temporal rules, computations, and outputs.
4.  **Temporal integrity** --- contemporaneous inputs and retrospective
    outcome information are structurally distinguishable.
5.  **Method extensibility** --- analytical methods are registry-backed
    replaceable modules, not hard-coded engine branches.
6.  **Shared deterministic computation** --- Analysis may invoke the
    existing governed Deterministic Computation Library without owning
    or duplicating it.
7.  **Selective durability** --- transient calculations remain cache;
    material evidence and Findings become Nexus artifacts.
8.  **Explicit failure semantics** --- execution failure, missing
    evidence, missing capability, incompatibility, and scientific
    outcomes remain distinct.
9.  **Retry determinism** --- deterministic scientific content can be
    recomputed and reconciled without runtime telemetry changing
    immutable identity.
10. **Concurrency readiness** --- workers use task-local state and no
    mutable enterprise singleton research state.
11. **Clean v2 implementation** --- no legacy Engine 09 imports, storage
    assumptions, schemas, output formats, or orchestration.
12. **Vertical-slice first** --- implement the smallest architecturally
    complete path before expanding the method surface.

------------------------------------------------------------------------

## 3. Non-Goals

The initial Analysis Engine shall not:

-   autonomously invent unrestricted Research Plans;
-   perform Research Admission;
-   schedule other engines;
-   directly call external market-data providers;
-   read Intake private filesystem output;
-   write durable findings to arbitrary local paths;
-   use Research Cache as canonical storage;
-   promote Findings into canonical knowledge;
-   decide whether an entire research campaign has converged;
-   make portfolio or trade decisions;
-   reproduce the full legacy Engine 09 method inventory;
-   build the Market Discovery Engine;
-   embed a favored market hypothesis in engine logic.

------------------------------------------------------------------------

## 4. Package Layout

The initial implementation should use a small, explicit package surface:

``` text
Engines/
└── Analysis/
    ├── __init__.py
    ├── engine.py
    ├── models.py
    ├── context.py
    ├── compatibility.py
    ├── nexus_adapter.py
    ├── sample.py
    ├── temporal.py
    ├── overlap.py
    ├── cache.py
    ├── findings.py
    ├── validation.py
    ├── registry.py
    ├── execution.py
    ├── errors.py
    ├── cli.py
    └── methods/
        ├── __init__.py
        ├── base.py
        ├── foundation.py
        ├── descriptive.py
        ├── comparison.py
        ├── relationship.py
        └── reliability.py
```

Supporting governed artifacts should live outside the engine package:

``` text
Governance/
├── Registries/
│   └── ANALYSIS_METHOD_LIBRARY.csv
└── Schemas/
    ├── analysis_task.schema.json
    ├── scientific_execution_context.schema.json
    ├── analysis_execution.schema.json
    ├── analysis_evidence.schema.json
    ├── analysis_finding.schema.json
    ├── analysis_missing_evidence.schema.json
    └── analysis_missing_capability.schema.json

Tests/
├── analysis_engine/
├── analysis_nexus/
├── analysis_scientific/
└── contracts/
```

The exact filenames may be adjusted to existing v2 naming conventions,
but responsibility boundaries must remain intact.

------------------------------------------------------------------------

## 5. Core Runtime Objects

### 5.1 AnalysisTask

`AnalysisTask` is the executable instruction accepted by the engine.

Minimum conceptual fields:

``` text
task_id
task_version
task_type = ANALYSIS
research_plan_ref
question_ref
input_artifact_refs[]
requested_objective
requested_method_ids[]
allowed_method_families[]
method_selection_policy
scope
sample_spec
temporal_spec
overlap_spec
outcome_spec
comparison_spec
required_evaluation_criteria
stopping_conditions
configuration
random_seed
authority_metadata
```

Rules:

-   `task_id` is not scientific identity by itself.
-   The task must reference governed inputs rather than local paths.
-   The task may prescribe exact methods or bounded method-selection
    authority.
-   Unsupported or unauthorized widening of scope must fail explicitly.
-   Task parsing must not infer missing scientific instructions that
    materially alter the question.

### 5.2 ScientificExecutionContext

The context is the immutable scientific execution specification
constructed from the admitted task plus resolved governed references.

Conceptual model:

``` text
ScientificExecutionContext
├── task_id
├── research_plan_ref
├── question_ref
├── input_artifact_refs
├── as_of_time
├── universe_scope
├── date_range
├── eligible_population
├── sample_construction_rule
├── exclusion_rule
├── event_or_opportunity_definition
├── comparison_or_control_definition
├── overlap_policy
├── future_information_policy
├── research_mode
├── discovery_interval
├── validation_interval
├── holdout_interval
├── method_specs
├── deterministic_computation_specs
├── parameters
├── random_seed
└── software_version
```

The context must be serializable into canonical content suitable for
provenance.

It must not contain transient worker paths, elapsed runtime, CPU
identity, or other operational telemetry in its scientific identity.

### 5.3 ResolvedInput

Represents one Nexus-resolved governed input:

``` text
artifact_ref
artifact_type
schema_name
schema_version
payload
integrity_state
provenance_summary
```

Analysis logic consumes `ResolvedInput`, not filesystem locations.

### 5.4 CompatibilityAssessment

``` text
state
method_id
reasons[]
missing_inputs[]
missing_measurements[]
sample_observations
temporal_conflicts[]
holdout_conflicts[]
capability_gaps[]
valid_alternatives[]
```

Allowed initial states:

``` text
COMPATIBLE
NOT_APPLICABLE
MISSING_INPUT
MISSING_MEASUREMENT
INSUFFICIENT_SAMPLE
TEMPORAL_CONFLICT
HOLDOUT_CONFLICT
UNSUPPORTED_METHOD
MISSING_CAPABILITY
INVALID_SCOPE
```

### 5.5 AnalysisExecutionRecord

Records execution facts without conflating them with scientific
conclusions:

``` text
execution_id
task_ref
context_fingerprint
engine_version
method_executions[]
input_refs[]
output_refs[]
execution_state
started_at
completed_at
retry_of
limitations[]
```

Operational telemetry may be recorded separately but must not
contaminate canonical scientific payload identity.

### 5.6 AnalysisEvidence

A durable evidence artifact contains method-level empirical results
required for lineage, audit, contradiction preservation,
reproducibility, or Finding support.

### 5.7 AnalysisFinding

A Finding is a bounded scientific proposition supported by one Analysis
execution.

Minimum conceptual content:

``` text
finding_id
task_ref
research_plan_ref
question_ref
input_artifact_refs
method_id
method_version
sample_definition
result_proposition
effect_or_magnitude
uncertainty
supporting_evidence_refs
contradictory_evidence_refs
applicability
limitations
temporal_scope
validation_state
research_mode
producer
created_at
```

A Finding is not canonical knowledge.

------------------------------------------------------------------------

## 6. Engine Facade

The public engine surface should remain narrow.

Conceptual Python interface:

``` python
class AnalysisEngine:
    def assess(self, task: AnalysisTask) -> CompatibilityAssessment:
        ...

    def run(self, task: AnalysisTask, *, publish: bool = True) -> AnalysisTaskResult:
        ...
```

`run()` owns orchestration only within the Analysis authority boundary.

It should delegate scientific behavior to explicit components rather
than accumulating method-specific logic.

Conceptual execution:

``` text
validate task contract
→ resolve Nexus inputs
→ construct Scientific Execution Context
→ validate temporal/authority constraints
→ resolve requested/allowed methods
→ assess compatibility
→ construct sample
→ resolve deterministic measurement requirements
→ execute method graph
→ validate results
→ classify transient vs durable outputs
→ construct evidence/findings
→ publish durable outputs
→ return task result
```

The engine facade must not:

-   choose new research questions;
-   create system-level tasks;
-   fetch unavailable external data;
-   silently substitute materially different methods;
-   decide campaign convergence.

------------------------------------------------------------------------

## 7. Research Nexus Adapter

### 7.1 Responsibility

`nexus_adapter.py` isolates the Analysis Engine from Research Nexus
implementation details.

It should provide semantic operations such as:

``` python
resolve_artifact(ref)
resolve_artifacts(refs)
publish_execution(record)
publish_evidence(evidence)
publish_finding(finding)
publish_missing_evidence(report)
publish_missing_capability(report)
verify_artifact(ref)
```

The adapter must use stable Research Nexus interfaces already present in
v2.

### 7.2 Prohibited Coupling

Analysis must not know:

-   Nexus database implementation;
-   payload filesystem layout;
-   SQLite tables;
-   object-store paths;
-   Intake staging directories;
-   Warehouse private paths.

### 7.3 Publication Identity

Canonical scientific payload identity must exclude non-semantic runtime
values.

Examples that must normally be excluded:

``` text
elapsed_seconds
worker_id
process_id
temporary_path
memory_usage
cpu_usage
local_cache_path
```

This follows the same scientific principle already proven in the
Intake/Nexus deterministic retry work: recomputation may take a
different amount of time without becoming different scientific content.

------------------------------------------------------------------------

## 8. Method Plugin Contract

### 8.1 AnalysisMethod

Every method implementation should satisfy a common protocol.

Conceptually:

``` python
class AnalysisMethod(Protocol):
    method_id: str
    version: str

    def assess(
        self,
        context: ScientificExecutionContext,
        inputs: AnalysisInputs,
    ) -> CompatibilityAssessment:
        ...

    def execute(
        self,
        context: ScientificExecutionContext,
        inputs: AnalysisInputs,
        services: AnalysisServices,
    ) -> MethodResult:
        ...

    def validate(
        self,
        result: MethodResult,
        context: ScientificExecutionContext,
    ) -> MethodValidationResult:
        ...
```

Methods receive services explicitly. They do not reach into global
engine state.

### 8.2 MethodResult

A method result should distinguish:

``` text
scientific_result
candidate_intermediates
durable_evidence_candidates
finding_candidates
limitations
warnings
deterministic_computations_used
sample_record
```

The method does not directly decide what becomes canonical knowledge.

### 8.3 Method Registry

`Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY.csv` should be the
governed capability registry.

Required registry fields should include:

``` text
method_id
method_name
method_family
version
status
required_inputs
optional_inputs
required_measurements
compatible_artifact_types
minimum_sample
temporal_requirements
future_information_allowance
research_mode_compatibility
parameters
outputs
validation_rules
determinism
random_seed_requirement
resource_profile
implementation_reference
```

Registry status is capability metadata, not execution authority.

### 8.3A Existing Legacy-Seed Registry

The existing `Governance/Registries/Tool-System/ANALYSIS_METHOD_LIBRARY.csv`
contains legacy-seed method concepts and `A09-*` identities derived from
legacy Engine 09.

That file is useful as migration/reference evidence for scientific capability
coverage, but its legacy identities and current minimal column structure SHALL
NOT define the executable v2 Analysis method contract.

Before Analysis method execution is implemented, the production registry SHALL
be normalized to clean v2 method identities and the governed fields required by
this technical design.

Legacy source mapping, if preservation is useful for audit/migration history,
shall remain metadata or a separate migration record and shall not create a
runtime dependency on legacy Engine 09 software.

### 8.4 Initial Methods

The first executable set should be deliberately small:

``` text
FOUNDATION_DATASET_INTROSPECTION
DESCRIPTIVE_STATISTICS
COHORT_OUTCOME_COMPARISON
RELATIONSHIP_REDUNDANCY
BASIC_STATISTICAL_RELIABILITY
```

Future-price geometry may be implemented as a governed deterministic
computation or bounded analytical capability according to the existing
Deterministic Computation Bank classification, but its retrospective
nature must be explicit.

------------------------------------------------------------------------

## 9. Method Resolution

`registry.py` and `execution.py` should resolve a bounded local method
graph.

Resolution rules:

1.  Exact task-specified method IDs take precedence.
2.  If the task grants a method family, only active compatible methods
    in that family are eligible.
3.  If bounded selection authority is granted, selection must be
    deterministic and inspectable where practical.
4.  Required method dependencies may execute locally only when they
    remain within the same Analysis task and authority boundary.
5.  Dependencies requiring another engine, external acquisition,
    separate admission, materially independent work, or a separate
    resource class must be returned as task-level dependencies for Task
    Manager.
6.  No method may widen the research objective merely because additional
    interesting relationships are visible.

------------------------------------------------------------------------

## 10. Shared Deterministic Computation Integration

### 10.1 Boundary

Analysis uses the existing shared `Core/deterministic_computation/`
capability.

It must not create an Analysis-owned duplicate indicator library.

### 10.2 Resolution Algorithm

For each method requirement:

``` text
required measurement already present and valid
    → use materialized measurement

required deterministic fact absent but derivable from governed input
    → invoke shared Deterministic Computation Library

required analytical transformation
    → execute Analysis method

required source data absent
    → MISSING_EVIDENCE or MISSING_CAPABILITY
```

### 10.3 Provenance

Every invoked deterministic computation must preserve:

``` text
computation_id
version
parameters
input artifact/ref or sample identity
output column/artifact identity
semantic fingerprint where applicable
```

### 10.4 No Intake Limitation

The implementation must contain no logic equivalent to:

``` python
if measurement not in intake_columns:
    fail_permanently()
```

Absence from routine Intake materialization is not absence of system
capability.

------------------------------------------------------------------------

## 11. Sample Construction Service

`sample.py` owns deterministic, reproducible sample construction.

### 11.1 SampleSpecification

Conceptual fields:

``` text
eligible_universe
date_range
inclusion_rules[]
exclusion_rules[]
event_definition
outcome_definition
comparison_definition
missing_data_policy
overlap_policy
selection_information_policy
research_mode
```

### 11.2 SampleRecord

Every material execution should produce a sample record containing:

``` text
eligible_count
included_count
excluded_count
exclusion_counts_by_reason
included_observation_identity
time_range
group/cohort membership
missing_data treatment
overlap treatment
future_information usage
sample_fingerprint
```

For large samples, observation identity may be represented by a
deterministic manifest/fingerprint rather than duplicating the entire
dataset into every Finding.

### 11.3 Scientific Rule

Sample construction is methodology.

It must therefore be versioned, inspectable, and reproducible.

------------------------------------------------------------------------

## 12. Temporal Integrity Service

`temporal.py` enforces separation between information available at
evaluation time and retrospective outcomes.

### 12.1 Information Classes

At minimum:

``` text
CONTEMPORANEOUS
RETROSPECTIVE_OUTCOME
STATIC_REFERENCE
```

### 12.2 Enforcement

The temporal validator must be capable of rejecting:

-   retrospective outcome columns used as predictor/input features;
-   validation or holdout observations used during protected
    discovery/training;
-   samples selected using future outcomes when the task claims
    contemporaneous selection;
-   repeated adaptation against a nominal holdout while continuing to
    label it holdout.

### 12.3 Retrospective Geometry

Future return, MFE, MAE, threshold timing, and path geometry are valid
historical outcome evidence when explicitly designated retrospective.

They must never silently become contemporaneous features.

------------------------------------------------------------------------

## 13. Overlap Service

`overlap.py` implements governed event/window overlap behavior.

Initial supported policies should include:

``` text
ALLOW
FIRST_QUALIFYING_WINS
HIGHEST_MAGNITUDE_WINS
CHRONOLOGICAL_EXCLUSION_WINDOW
NON_OVERLAPPING_INTERVALS
```

Each policy must be deterministic for identical inputs/configuration.

The selected policy and version belong in the Scientific Execution
Context and sample provenance.

Methods must not change overlap policy after observing results unless
the task explicitly authorizes a new exploratory specification, in which
case the change must be represented as a new specification rather than
hidden mutation.

------------------------------------------------------------------------

## 14. Research Mode and Holdout Protection

The context must declare one of:

``` text
EXPLORATORY
CONFIRMATORY
VALIDATION
REPLICATION
ROBUSTNESS
RETROSPECTIVE_CHARACTERIZATION
```

Protected intervals should be explicit objects rather than conventions
embedded in method code.

Conceptually:

``` text
discovery_interval
validation_interval
holdout_interval
```

A method claiming confirmatory or validation evidence must verify that
its data use is compatible with the protected interval designation.

If not, return `HOLDOUT_CONFLICT` or `TEMPORAL_CONFLICT`.

------------------------------------------------------------------------

## 15. Research Cache

### 15.1 Purpose

Research Cache stores replaceable task-local working products.

Examples:

-   temporary joined tables;
-   matrices;
-   decompressed datasets;
-   intermediate statistics;
-   temporary cohort tables;
-   exploratory rankings;
-   repeated-computation acceleration products.

### 15.2 Initial Implementation

The first implementation may use a filesystem-backed task-local cache:

``` text
<configured_analysis_cache_root>/
└── <execution_id>/
    ├── manifest.json
    └── ...
```

The root must come from configuration, not scientific identity.

No durable artifact may depend on the physical cache path.

### 15.3 Cache Interface

Conceptually:

``` python
class ResearchCache:
    def put(self, key, value, metadata=None): ...
    def get(self, key): ...
    def exists(self, key): ...
    def delete(self, key): ...
    def clear_execution(self, execution_id): ...
```

### 15.4 Promotion

Cache content may become durable only through explicit artifact
construction, validation, governed identity assignment, and Research
Nexus publication.

Moving/copying a cache file into a durable directory is not promotion.

------------------------------------------------------------------------

## 16. Evidence and Finding Construction

`findings.py` converts validated method outputs into canonical artifact
payloads.

### 16.1 Separation

``` text
MethodResult
    ≠
Evidence artifact
    ≠
Finding
    ≠
Knowledge Candidate
    ≠
Canonical Knowledge
```

### 16.2 Evidence

Evidence should preserve objective method-level outputs needed to
support or contradict propositions.

### 16.3 Finding

A Finding should state a bounded proposition such as:

``` text
Within the defined sample and temporal scope, measurement X showed
effect Y under method M, with uncertainty U and limitations L.
```

It must not state:

``` text
MTS now knows X is universally true.
```

### 16.4 Contradiction Preservation

Contradictory evidence is first-class scientific output.

Finding construction must allow both supporting and contradictory
evidence references.

------------------------------------------------------------------------

## 17. Canonical Serialization and Fingerprints

Scientific identity should be derived from canonical semantic content.

At minimum, canonicalization should:

-   use stable key ordering;
-   normalize timestamp representation;
-   normalize null representation;
-   reject non-finite numbers unless explicitly governed;
-   preserve method/computation versions;
-   preserve parameter values;
-   preserve sample and temporal specifications;
-   exclude operational telemetry;
-   produce deterministic bytes for deterministic content.

Useful fingerprints:

``` text
context_fingerprint
sample_fingerprint
method_execution_fingerprint
finding_semantic_fingerprint
```

Fingerprint functions should be centralized and tested.

------------------------------------------------------------------------

## 18. Validation Pipeline

Before publication, durable output should pass:

``` text
schema validation
→ controlled vocabulary validation
→ reference validation
→ scientific context completeness
→ temporal integrity validation
→ provenance validation
→ method-output validation
→ canonical serialization validation
→ publication
```

Validation failure is an execution failure or blocked publication, not a
negative scientific finding.

------------------------------------------------------------------------

## 19. Failure Model

### 19.1 Execution States

``` text
SUCCEEDED
FAILED
BLOCKED
CANCELLED
NOT_APPLICABLE
RETRYABLE_FAILURE
```

### 19.2 Scientific Outcomes

Initial bounded vocabulary:

``` text
SUPPORTED
NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
UNSTABLE
MISSING_CAPABILITY
```

Where the more descriptive architecture vocabulary is required,
Finding/report schemas may additionally preserve:

``` text
SUPPORTED_BY_THIS_ANALYSIS
NOT_SUPPORTED_BY_THIS_ANALYSIS
CONTRADICTORY_EVIDENCE
MISSING_INPUT
METHOD_NOT_APPLICABLE
GENERALIZATION_FAILURE
```

The schema should avoid ambiguous overlap by defining which vocabulary
applies to execution summaries versus Findings.

### 19.3 Missing Evidence

Return a structured report:

``` text
required_input
reason
affected_question
valid_alternative_available
scientific_consequence
```

### 19.4 Missing Capability

Return:

``` text
missing_capability
why_required
affected_task
available_alternatives
scientific_consequence
```

No silent substitution.

------------------------------------------------------------------------

## 20. AnalysisTaskResult

The engine should return a compact task-level result to its caller:

``` text
task_id
execution_id
execution_state
compatibility_state
scientific_outcomes[]
published_artifact_refs[]
finding_refs[]
evidence_refs[]
missing_evidence_refs[]
missing_capability_refs[]
limitations[]
retry_metadata
```

This is a routing/execution result.

It is not a substitute for durable scientific artifacts.

------------------------------------------------------------------------

## 21. Authority Enforcement

Authority checks should occur before scientific execution.

Analysis may:

-   resolve authorized Nexus inputs;
-   execute admitted work;
-   invoke approved deterministic computations;
-   execute approved methods;
-   create task-local cache;
-   publish authorized evidence/Findings;
-   report gaps.

Analysis must reject or return blocked status for attempts to:

-   widen the Research Plan without authority;
-   bypass Research Admission;
-   acquire external data;
-   alter governance;
-   schedule unrelated work;
-   promote knowledge;
-   issue investment Decisions;
-   execute trades;
-   erase contradictory durable evidence.

Authority enforcement belongs in explicit code and contract tests, not
documentation alone.

------------------------------------------------------------------------

## 22. Concurrency Model

The engine core should be worker-safe from the first implementation.

Rules:

1.  No mutable global research state.
2.  Each execution receives an isolated `ScientificExecutionContext`.
3.  Each execution receives an isolated Research Cache namespace.
4.  Method instances should be stateless or task-local.
5.  Nexus publication must tolerate concurrent independent tasks.
6.  Deterministic computation services must be invoked through
    concurrency-safe interfaces.
7.  Task Manager, not Analysis, decides global worker allocation.
8.  Analysis may expose resource declarations from the method registry.

The first laptop implementation may execute synchronously while
preserving these boundaries.

Synchronous execution is an implementation mode, not an architectural
commitment.

------------------------------------------------------------------------

## 23. Configuration

Configuration should be explicit and environment-independent where
possible.

Initial configuration may include:

``` text
analysis_cache_root
max_in_memory_rows
default_chunk_size
canonical_float_policy
schema_registry_location
method_registry_location
engine_version
cache_retention_policy
```

Scientific parameters belong in the task/context, not hidden application
defaults, whenever changing them could change the scientific result.

------------------------------------------------------------------------

## 24. Logging and Operational Telemetry

Operational logs should record:

-   execution lifecycle;
-   method lifecycle;
-   Nexus retrieval/publication;
-   cache operations;
-   validation failures;
-   retry/reconciliation;
-   resource warnings.

Logs must not be the only record of scientific methodology or material
results.

Operational telemetry must remain outside immutable scientific payload
identity unless explicitly governed otherwise.

------------------------------------------------------------------------

## 25. Initial Analysis Method Details

### 25.1 Foundation / Dataset Introspection

Inputs:

``` text
NORMALIZED_DATASET
```

Produces:

``` text
row_count
columns
data types
date coverage
instrument coverage
missingness
available deterministic measurements
outcome-column inventory
duplicate/ordering observations
method compatibility facts
```

This method should be deterministic.

### 25.2 Descriptive Statistics

Initial support:

-   count;
-   missing count;
-   mean;
-   median;
-   standard deviation;
-   minimum/maximum;
-   selected quantiles;
-   group counts;
-   basic distribution summaries.

It should avoid presenting descriptive statistics as predictive
evidence.

### 25.3 Cohort / Outcome Comparison

Given governed group definitions, produce:

-   group counts;
-   outcome distributions;
-   differences in central tendency;
-   differences in rates/proportions where applicable;
-   effect magnitude;
-   uncertainty supported by the selected reliability method;
-   explicit sample definitions.

### 25.4 Relationship / Redundancy

Initial support may include:

-   Pearson correlation where assumptions/scope permit;
-   Spearman rank correlation;
-   pairwise missingness accounting;
-   simple redundancy flags based on governed thresholds only when a
    task specifies or governance defines those thresholds.

Correlation is evidence of relationship, not automatic feature value.

### 25.5 Basic Statistical Reliability

Initial support should focus on transparent, inspectable evidence rather
than a broad statistical package.

Possible first capabilities:

-   confidence intervals for means/proportions where appropriate;
-   bootstrap intervals when explicitly configured;
-   sample-size reporting;
-   sensitivity to subgroup size;
-   effect-size reporting.

Any stochastic resampling must preserve the seed.

------------------------------------------------------------------------

## 26. Future Price Geometry

Future-price geometry is explicitly retrospective.

For an origin timestamp `T`, governed calculations may include:

``` text
forward_return(horizon)
maximum_favorable_excursion(horizon)
maximum_adverse_excursion(horizon)
time_to_mfe
time_to_mae
first_threshold_hit
path_summary
```

Rules:

-   origin information and future path information must be structurally
    separated;
-   geometry columns must be marked retrospective;
-   geometry may define or characterize historical outcome regions when
    the Research Plan authorizes it;
-   geometry must not be exposed as if known at `T`;
-   geometry does not itself define a trade signal or stop.

------------------------------------------------------------------------

## 27. First Vertical Slice Specification

The first implementation proof should use the already proven real
Intake-published historical market dataset path.

The vertical slice shall prove:

``` text
real historical source
    ↓
Intake
    ↓
Research Nexus NORMALIZED_DATASET
    ↓
governed AnalysisTask
    ↓
Analysis Nexus resolution
    ↓
ScientificExecutionContext
    ↓
Foundation Dataset Introspection
    ↓
Descriptive Statistics
    ↓
one governed cohort/comparison operation
    ↓
optional additional deterministic computation
    ↓
validated Evidence
    ↓
validated Finding
    ↓
Research Nexus publication
    ↓
retrieval
    ↓
integrity verification
    ↓
fresh recomputation retry
    ↓
same canonical scientific identity / reconciled publication
```

### 27.1 Required Proof Assertions

The proof must assert:

``` text
input_resolved_from_nexus == True
private_intake_path_used == False
context_valid == True
sample_reproducible == True
temporal_integrity == PASSED
method_registry_resolution == PASSED
method_version_preserved == True
deterministic_library_access == PASSED
cache_is_transient == True
finding_schema_valid == True
finding_retrievable == True
finding_integrity_verification == PASSED
fresh_retry_semantically_identical == True
fresh_retry_reconciled == True
```

### 27.2 Preferred Initial Dataset

The existing SMH Intake/Nexus proof dataset is suitable because it is
real historical data already used to prove the Intake vertical boundary.

The Analysis proof must consume the Nexus artifact reference, not the
original SMH parquet path.

------------------------------------------------------------------------

## 28. Vertical Slice Scientific Task

The first task should remain scientifically modest.

Recommended objective:

``` text
Characterize the governed SMH historical dataset, construct a reproducible
time-bounded sample, summarize selected contemporaneous measurements, and
compare a defined retrospective outcome cohort with a defined control cohort.
```

This proves Analysis mechanics without pretending the first execution
answers a major trading hypothesis.

A later experiment may test hypotheses such as:

``` text
SMA 20 > SMA 50 > SMA 200
+
increasing volume
+
relatively stable price
```

but that hypothesis must enter through a Research Plan/task and must not
be hard-coded into Analysis.

------------------------------------------------------------------------

## 29. Schema Plan

### 29.1 `analysis_task.schema.json`

Validates executable governed task structure.

### 29.2 `scientific_execution_context.schema.json`

Validates reproducibility-critical context.

### 29.3 `analysis_execution.schema.json`

Validates task execution record and execution state.

### 29.4 `analysis_evidence.schema.json`

Validates durable empirical evidence.

### 29.5 `analysis_finding.schema.json`

Validates bounded Findings.

### 29.6 Gap Schemas

Separate schemas should exist for:

``` text
analysis_missing_evidence.schema.json
analysis_missing_capability.schema.json
```

unless existing v2 artifact governance provides canonical generic
equivalents that should be reused.

Before creating new schemas, implementation must audit existing v2
schemas/contracts to avoid duplicating an already-governed artifact
type.

------------------------------------------------------------------------

## 30. Testing Plan

### 30.1 Unit Tests

``` text
Tests/analysis_engine/
```

Cover:

-   task parsing;
-   context construction;
-   method registry loading;
-   compatibility states;
-   sample construction;
-   exclusion accounting;
-   overlap policies;
-   temporal classification;
-   holdout conflict detection;
-   deterministic computation resolution;
-   method execution;
-   result validation;
-   cache lifecycle;
-   canonicalization;
-   Finding construction;
-   failure semantics.

### 30.2 Contract Tests

Extend existing contract tests for:

-   Analysis task schema;
-   Scientific Execution Context schema;
-   Analysis Evidence schema;
-   Finding schema;
-   controlled vocabulary;
-   Nexus artifact types;
-   relationship types;
-   required provenance.

### 30.3 Nexus Integration Tests

``` text
Tests/analysis_nexus/
```

Prove:

-   retrieval by artifact reference;
-   no local-path dependency;
-   publication;
-   retrieval after publication;
-   integrity verification;
-   immutable conflict behavior;
-   deterministic retry reconciliation.

### 30.4 Scientific Regression Tests

``` text
Tests/analysis_scientific/
```

Use synthetic datasets with known properties:

1.  known positive relationship;
2.  known null relationship;
3.  known contradictory relationship;
4.  intentionally leaked future feature;
5.  overlapping events;
6.  holdout contamination;
7.  missing required measurement that is derivable;
8.  missing source data that is not derivable;
9.  deterministic method retry;
10. seeded stochastic method retry.

Expected scientific behavior should be asserted independently from
runtime success.

### 30.5 End-to-End Proof

Run the real Intake-published SMH artifact through the first Analysis
vertical slice and write a human-readable proof report to Downloads for
inspection.

The report is evidence of the test run, not canonical scientific
storage.

------------------------------------------------------------------------

## 31. Implementation Sequence

Implementation should proceed in this order.

### Phase A --- Contracts and Models

1.  audit existing v2 artifact/task schemas;
2.  define only missing Analysis schemas;
3.  define controlled vocabulary additions;
4.  implement `models.py`;
5.  implement canonical serialization/fingerprints;
6.  add contract tests.

### Phase B --- Nexus Boundary

1.  implement `nexus_adapter.py`;
2.  retrieve an existing Intake-published `NORMALIZED_DATASET`;
3.  validate schema/integrity;
4.  add Analysis/Nexus retrieval tests.

### Phase C --- Scientific Context

1.  implement `context.py`;
2.  implement `temporal.py`;
3.  implement `overlap.py`;
4.  implement `sample.py`;
5.  add leakage/holdout/overlap tests.

### Phase D --- Method Infrastructure

1.  implement method protocol;
2.  implement registry loader;
3.  connect `ANALYSIS_METHOD_LIBRARY.csv`;
4.  implement compatibility service;
5.  implement execution service.

### Phase E --- Initial Methods

Implement and validate:

1.  Foundation Dataset Introspection;
2.  Descriptive Statistics;
3.  Cohort/Outcome Comparison;
4.  Relationship/Redundancy;
5.  Basic Statistical Reliability.

### Phase F --- Shared Deterministic Computation

1.  connect to `Core/deterministic_computation/`;
2.  prove use of already-materialized measurement;
3.  prove on-demand computation of a governed absent measurement;
4.  preserve computation provenance;
5.  prove Analysis remains independent of Intake materialization
    choices.

### Phase G --- Cache and Durable Output

1.  implement task-local Research Cache;
2.  implement evidence construction;
3.  implement Finding construction;
4.  implement output validation;
5.  publish through Nexus;
6.  retrieve and verify.

### Phase H --- Retry Proof

1.  execute task;
2.  publish Finding;
3.  fresh recomputation;
4.  confirm runtime telemetry differs where expected;
5.  confirm canonical scientific payload is identical;
6.  confirm same artifact identity/reconciliation behavior.

### Phase I --- Real Vertical Proof

Execute the complete real SMH path and produce an auditable report.

Only after this proof passes should the implementation expand toward the
Deterministic Measurement Convergence Campaign.

------------------------------------------------------------------------

## 32. Definition of Done --- Initial Analysis Engine

The first Analysis Engine implementation is complete only when all of
the following are true:

-   [ ] Analysis accepts a governed Analysis task.
-   [ ] Durable input is resolved through Research Nexus.
-   [ ] No Intake private path is required.
-   [ ] Scientific Execution Context is constructed and validated.
-   [ ] Temporal integrity is enforced.
-   [ ] Exploration/confirmation designation is preserved.
-   [ ] Sample construction is reproducible.
-   [ ] Overlap policy is explicit.
-   [ ] Analysis Method Library resolves methods by governed
    identity/version.
-   [ ] Initial method set executes through a common plugin contract.
-   [ ] Compatibility failures are explicit.
-   [ ] Shared Deterministic Computation Library can be invoked.
-   [ ] Analysis is not limited to Intake-materialized measurements.
-   [ ] Research Cache is task-local and non-authoritative.
-   [ ] Evidence and Findings are distinct from intermediates.
-   [ ] Findings preserve provenance, uncertainty, applicability, and
    limitations.
-   [ ] Contradictory evidence can be preserved.
-   [ ] Missing Evidence is structured.
-   [ ] Missing Capability is structured.
-   [ ] Execution state is distinct from scientific outcome.
-   [ ] Durable output publishes only through Research Nexus.
-   [ ] Published Finding can be retrieved and integrity-verified.
-   [ ] Fresh deterministic recomputation produces equivalent canonical
    scientific content.
-   [ ] Retry reconciles rather than creating conflicting immutable
    content.
-   [ ] Unit tests pass.
-   [ ] Contract tests pass.
-   [ ] Nexus integration tests pass.
-   [ ] scientific regression tests pass.
-   [ ] real SMH Analysis vertical proof passes.
-   [ ] `git diff --check` passes.
-   [ ] no legacy Engine 09 software dependency exists.

------------------------------------------------------------------------

## 33. Explicit Legacy Exclusion Test

Before the first Analysis implementation commit, run a repository audit
proving the new engine does not import or depend on legacy
Analysis/Engine 09 software.

The audit should search the new Analysis package and tests for:

``` text
Engine09
engine09
09-
legacy Analysis paths
old Research/ hierarchy
legacy warehouse imports
legacy schema names
legacy dataset loader imports
```

A textual resemblance in scientific concepts is not a dependency.

The test is intended to prevent accidental software inheritance while
allowing intentionally reimplemented scientific concepts required by v2
architecture.

------------------------------------------------------------------------

## 34. Deterministic Measurement Convergence Campaign Boundary

The campaign is a workload executed through this engine, not engine
architecture.

After the minimum vertical slice is proven:

``` text
five-ticker cohort
    ↓
governed Analysis tasks
    ↓
measurement contribution / redundancy / interaction / stability /
context / contradiction / generalization evidence
    ↓
Findings in Research Nexus
    ↓
Research Director Measurement Convergence Assessment
```

Analysis does not declare convergence.

Analysis does not permanently remove lower-ranked deterministic
computations.

Analysis does not turn measurement usage frequency into scientific
truth.

------------------------------------------------------------------------

## 35. Hypothesis Neutrality Requirement

No initial method, schema, registry, sample constructor, or engine
branch may privilege a specific market hypothesis.

The engine must be equally able to return:

``` text
SUPPORTED
NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
UNSTABLE
```

for any admitted hypothesis.

A hypothesis involving moving-average alignment, increasing volume, and
stable price may be an excellent first campaign question, but it remains
data-testable research content rather than infrastructure.

------------------------------------------------------------------------

## 36. Technical Decision

The v2 Analysis Engine shall be implemented as a small scientific
execution kernel surrounded by governed adapters and replaceable method
plugins.

Its core is:

``` text
task contract
+ Nexus boundary
+ Scientific Execution Context
+ sample/temporal integrity
+ method registry
+ shared deterministic computation
+ bounded method execution
+ transient Research Cache
+ evidence/Finding construction
+ canonical publication/retry
```

Everything else should remain replaceable.

The engine should become more analytically capable by adding governed
methods and computations, not by increasing hidden authority or
coupling.

> **Analysis answers the admitted empirical question with reproducible
> evidence. It does not decide what MTS should believe, research next,
> or trade.**
