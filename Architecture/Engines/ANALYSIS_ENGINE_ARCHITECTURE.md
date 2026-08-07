# Momentum Trading System — Analysis Engine Architecture

**Status:** Proposed
**Authority:** Engine-specific architecture subordinate to `CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`, `Architecture/ENGINE_ARCHITECTURE.md`, `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`, and governing Research/Data/Artifact standards and policies
**Engine Name:** Analysis Engine
**Governance Role:** Historical/scientific empirical analysis
**Distinct From:** Market Discovery Engine, Research Director, Data Intake Engine, Decision Engine, Accountability Engine, Task Manager, and Research Nexus

---

## 1. Purpose

The Analysis Engine converts governed data and research inputs into reproducible empirical evidence and bounded analytical findings.

Its purpose is to answer **assigned analytical questions** by performing scientific and statistical work against governed datasets, not to decide what MTS should research next.

The Analysis Engine may:

- inspect governed datasets;
- characterize samples, regimes, events, and outcomes;
- compare groups and conditions;
- quantify relationships;
- evaluate feature contribution and redundancy;
- test robustness and stability;
- evaluate temporal behavior;
- evaluate economic relevance;
- identify contradictions;
- evaluate generalization;
- discover candidate relationships, interactions, contexts, and anomalies when exploratory work is authorized;
- invoke governed deterministic computations when required;
- create temporary analytical working products;
- publish governed evidence and findings through the Research Nexus.

The Analysis Engine must not:

- own research intent;
- create its own unrestricted research agenda;
- replace the Research Director;
- schedule itself or other engines;
- bypass Accountability admission requirements;
- acquire external data outside Data Intake governance;
- treat every computed result as durable knowledge;
- promote its own findings to canonical knowledge;
- make investment decisions;
- execute trades;
- own enterprise durable state.

The governing principle is:

> **Research Director decides what must be learned. Task Manager makes the work happen. Analysis performs the bounded empirical work. Research Nexus preserves durable governed results.**

---

## 2. Relationship to Discovery and Market Discovery

The **Analysis Engine** is the historical/scientific empirical engine of MTS.

Discovery remains a valid scientific concept: Analysis may discover relationships, interactions, anomalies, contexts, contradictions, and candidate explanatory structures when authorized by governed research.

Discovery is not a separate historical engine or authority role.

The **Market Discovery Engine** is architecturally separate. It searches current/live market state for conditions, patterns, candidates, opportunities, anomalies, and research-worthy phenomena.

### Analysis Engine

Asks:

> “Given this governed question, dataset, scope, and method, what does the evidence show?”

Its work is primarily historical, empirical, statistical, comparative, analytical, and research-oriented.

### Market Discovery Engine

Asks:

> “Where in the current/live market is something happening that deserves evaluation?”

Its work is primarily current-state scanning, anomaly/event detection, and candidate discovery.

The engines may share libraries and governed methods where appropriate, but they are architecturally distinct.

---

## 3. Architectural Position

The canonical research path is:

```text
Question / Knowledge Gap
        ↓
Research Director
        ↓
Proposed Research Plan
        ↓
Accountability — Research Admission
        ↓
Task Manager
        ↓
Analysis Engine
        ↓
Research Nexus
        ↓
Research Director
        ↓
Follow-up / Convergence / Knowledge Candidate
```

The Analysis Engine does not receive private instructions directly from another engine implementation.

Its executable work must arrive through governed task contracts and governed Nexus references.

There is no canonical:

```text
Intake → Analysis
```

handoff.

The canonical relationship is:

```text
Intake
  ↓
Research Nexus
  ↓
governed task + Nexus input references
  ↓
Analysis
```

---

## 4. Core Responsibility Boundary

The Analysis Engine owns **bounded empirical execution**.

It does not own:

- the scientific question;
- admission authority;
- global task scheduling;
- canonical research-state storage;
- knowledge promotion;
- portfolio intent;
- live trade authority.

For every task, Analysis must be able to state:

```text
what was requested
what inputs were used
what methods were used
what computations were added
what population/sample was analyzed
what temporal rules applied
what evidence was produced
what uncertainty or limitation exists
what could not be answered
```

---

## 5. Inputs

Analysis consumes governed task instructions and Nexus-resolved artifacts.

Possible inputs include:

- normalized market-history datasets;
- deterministic measurements materialized by Intake;
- event/observation datasets;
- research-question references;
- Research Plan references;
- task-specific scope;
- sample definitions;
- cohort definitions;
- outcome definitions;
- comparison/control definitions;
- temporal boundaries;
- holdout definitions;
- overlap rules;
- approved method identifiers and versions;
- required evaluation criteria;
- stopping conditions relevant to the bounded task;
- prior evidence/findings where explicitly referenced;
- approved configuration and random seed where applicable.

Analysis must not depend on another engine's private directory structure.

Physical Research Nexus paths must not be embedded in Analysis logic.

---

## 6. Scientific Execution Context

Every material analytical execution must operate under an explicit **Scientific Execution Context**.

At minimum, when applicable, the context should preserve:

```text
task_id
research_plan_ref
question_ref
input_artifact_refs
as_of_time
instrument / universe scope
date range
eligible population
sample construction rule
exclusion rule
event / opportunity definition
comparison / control definition
overlap policy
future-information policy
exploration / confirmation designation
training / discovery interval
validation interval
holdout interval
method ids / versions
deterministic computation ids / versions
parameters / configuration
random seed
software version
```

Not every field applies to every method, but material research must preserve enough context to reproduce the result and detect scientific leakage.

---

## 7. Temporal Integrity

Analysis must explicitly distinguish between:

### Contemporaneous information

Information available at or before the timestamp being evaluated.

### Retrospective outcome information

Information that became available after the evaluated timestamp and is used only to characterize what happened later.

Future information may be used for historical outcome construction and retrospective geometry.

Future information must not be presented as though it was available to a simulated historical decision.

For example:

```text
At timestamp T:
    contemporaneous measurements → may be inputs

After timestamp T:
    future return / excursion / path → may be outcome evidence

The latter may evaluate the former.
The latter may not be smuggled into the former.
```

---

## 8. Exploration vs Confirmation

Analysis must preserve whether work is:

- exploratory;
- confirmatory;
- validation;
- replication;
- robustness testing;
- retrospective characterization.

Exploratory search may discover hypotheses.

Exploratory discoveries do not become confirmed findings merely because they are statistically interesting.

When confirmatory inference is claimed, the hypothesis, evaluation criteria, and protected evidence boundary must have been established before examining the evidence intended to test the claim.

Repeated adaptation to the same nominal holdout destroys holdout status.

---

## 9. Sample Construction

Material Analysis must preserve how the sample was constructed.

It should be possible to reconstruct:

- eligible universe;
- included observations;
- excluded observations;
- exclusion reasons;
- time range;
- event or outcome definition;
- control/comparison construction;
- overlap treatment;
- missing-data handling;
- whether future information was used in selection;
- whether the sample is exploratory or confirmatory.

Sample construction is part of scientific methodology, not an incidental implementation detail.

---

## 10. Overlap

Research involving events, opportunities, paths, episodes, or windows must define overlap behavior.

Possible governed behaviors may include:

- allow overlapping observations;
- first qualifying event wins;
- highest-magnitude event wins;
- chronological exclusion window;
- event-family-specific exclusion;
- non-overlapping interval construction.

The selected rule must be deterministic where possible and preserved in methodology/provenance.

Analysis must not silently change overlap rules to improve results.

---

## 11. Shared Deterministic Computation Library

The governed Deterministic Computation Library is a **shared system resource**.

It is not owned by Intake.

It is not owned by Analysis.

Analysis may invoke the library when:

- the required measurement was not materialized by Intake;
- different governed parameters are required;
- a measurement must be recomputed against another valid dataset;
- an analytical method requires an intermediate deterministic transformation;
- retrospective analysis requires a governed deterministic computation not routinely materialized.

Analysis is therefore **never limited to the columns Intake happened to materialize**.

This separation is permanent:

```text
availability of deterministic computation
    ≠
routine Intake materialization
```

---

## 12. Deterministic Computation vs Analytical Method

A deterministic computation produces reproducible mathematical facts from defined inputs.

Examples:

- SMA;
- EMA;
- ATR;
- rolling return;
- volume z-score;
- slope;
- range position;
- future excursion geometry when explicitly retrospective.

An analytical method evaluates relationships, contribution, uncertainty, stability, context, or meaning.

Examples:

- outcome comparison;
- predictive validation;
- incremental contribution;
- redundancy analysis;
- interaction analysis;
- robustness testing;
- contradiction testing;
- economic significance analysis;
- generalization testing.

The architecture must keep these concepts separate even when they execute in the same worker process.

---

## 13. Analysis Method Library

MTS shall maintain a governed **Analysis Method Library** separate from the Deterministic Computation Library.

The initial method families should include, at minimum:

### Foundation / Dataset Introspection

Determines:

- available columns;
- row count;
- temporal coverage;
- sample structure;
- missingness;
- measurement availability;
- outcome availability;
- compatibility with requested methods.

### Descriptive Analysis

Characterizes distributions, frequencies, central tendency, dispersion, tails, regimes, event counts, and other descriptive properties.

### Outcome Comparison

Compares defined cohorts, conditions, successes/failures, events/non-events, opportunity regions/controls, and other governed groups.

### Statistical Reliability

Evaluates uncertainty, sampling variability, confidence intervals or equivalent evidence, sensitivity to sample size, and other applicable statistical reliability properties.

### Predictive Validation

Evaluates whether information available at the evaluated timestamp has out-of-sample or otherwise properly protected association with later outcomes.

### Incremental Contribution

Evaluates whether a feature or measurement contributes information beyond other available features.

### Robustness Analysis

Evaluates sensitivity to:

- parameter changes;
- time periods;
- subgroups;
- regimes;
- outliers;
- alternative valid specifications;
- reasonable perturbations.

### Relationship / Redundancy Analysis

Evaluates:

- correlation;
- dependence;
- redundancy;
- shared information;
- conditional relationships;
- duplicated explanatory content.

### Interaction Analysis

Evaluates whether features matter jointly even when standalone contribution is weak.

### Economic Analysis

Evaluates economic magnitude and practical relevance separately from statistical significance.

### Contradiction Analysis

Actively searches for evidence inconsistent with a claimed relationship or apparent pattern.

### Generalization Analysis

Evaluates whether a result survives across instruments, periods, market conditions, sectors, asset classes, or other governed domains.

### Knowledge-Discovery Methods

When authorized exploratory research requires them, Analysis may execute bounded:

- relationship discovery;
- conditional discovery;
- interaction discovery;
- context discovery;
- anomaly discovery.

These methods produce **candidate evidence/findings**, not self-certified knowledge.

---

## 14. Method Registry Requirements

Each governed Analysis method should eventually declare:

```text
method_id
method_name
method_family
version
status
required_inputs
optional_inputs
required_measurements
compatible_artifact_types
minimum_sample requirements
temporal requirements
future-information allowance
exploration / confirmation compatibility
parameters
outputs
validation rules
determinism / stochasticity
random-seed requirements
resource profile
implementation reference
```

A method registry entry describes capability.

It does not grant authority.

---

## 15. Method Freedom and Extensibility

Analysis must not be limited forever to the initial method library.

A Research Plan may require a method not yet present.

Analysis may support creation or registration of a new analytical method when governed policy permits, but:

- the method must receive an identity/version;
- assumptions must be explicit;
- required inputs must be declared;
- validation behavior must be defined;
- provenance must identify the method/version;
- use in confirmatory research must respect research policy;
- an ad hoc successful result must not silently become a permanent production method.

The engine architecture should allow method plugins or equivalent replaceable modules without rebuilding the engine core.

---

## 16. Method Selection

The Research Director owns research intent.

The Research Plan should specify either:

- the required method;
- an allowed method family;
- the required evidentiary objective with bounded method-selection authority.

Analysis may choose among approved compatible implementations when the task grants that freedom.

Analysis must not transform:

> “Test whether X contributes beyond Y”

into:

> “Investigate whatever seems interesting.”

Method selection remains bounded by admitted research intent.

---

## 17. Compatibility Assessment

Before executing a method, Analysis should determine compatibility.

Possible compatibility states include:

```text
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

Compatibility assessment must not fabricate missing evidence.

Where a required deterministic measurement can validly be created from existing governed inputs, Analysis may invoke the shared computation library.

Where required source data does not exist, Analysis must return an explicit missing-data or missing-capability outcome rather than privately acquiring data.

---

## 18. Dependency Handling

Analysis methods may have logical dependencies.

However, Analysis must not become a hidden Task Manager.

A method may internally require another bounded analytical primitive, but system-level work dependencies belong in governed task planning/routing.

The architecture should prefer:

```text
Task declares required analytical objective
        ↓
Analysis resolves compatible approved method graph locally
        ↓
bounded execution
```

only where the dependency graph is internal to one Analysis task and one authority boundary.

If the dependency requires:

- another engine;
- external data acquisition;
- separate durable research admission;
- materially independent work;
- another worker or resource class;

the dependency belongs in Task Manager orchestration, not hidden Analysis execution.

---

## 19. Analysis Is Not Limited by Intake

Intake should provide broad factual context efficiently.

Analysis should use it.

But Analysis must never assume:

> “If Intake did not calculate it, I cannot investigate it.”

Instead:

```text
needed fact exists in Intake dataset
    → use governed measurement

needed deterministic fact derivable from existing governed data
    → invoke shared Deterministic Computation Library

needed analytical transformation
    → execute governed Analysis method

needed source data unavailable
    → explicit Missing Evidence / Missing Capability outcome

needed new research question
    → return evidence/gap to Research Director
```

---

## 20. Opportunity and Failure Characterization

When authorized by a Research Plan, Analysis may characterize historically relevant outcome regions.

This may include:

- proximal opportunity regions;
- positive outcome regions;
- negative outcome regions;
- comparable failures;
- liquidity-trap regions;
- false-signal regions;
- neutral/control regions;
- regime-specific outcomes;
- temporal path behavior.

Analysis must not call these “good trades” merely because future prices moved favorably.

Retrospective future-price geometry is evidence.

Trade desirability belongs to later research/decision logic under governed assumptions.

---

## 21. Future Price Geometry

When requested, Analysis may calculate retrospective future-price geometry from historical timestamps.

Examples include:

- maximum favorable excursion by horizon;
- maximum adverse excursion by horizon;
- time to excursion;
- ordering of favorable/adverse excursion;
- path to outcome;
- future-return distribution;
- volatility/range experienced;
- threshold-hit timing.

These are retrospective objective outcomes.

They do not, by themselves, define:

- entry signals;
- stop rules;
- risk/reward rules;
- trade quality;
- Decision authority.

Future geometry must be clearly labeled retrospective and must never contaminate contemporaneous feature inputs.

---

## 22. Liquidity-Trap and Failure Controls

Opportunity research must include appropriately defined failure/control evidence where material.

This is especially important where apparent momentum, volume, volatility, or trend conditions may also occur in:

- failed breakouts;
- liquidity traps;
- temporary squeezes;
- mean-reverting spikes;
- low-liquidity distortions;
- regime transitions.

ATR and other volatility/range measurements may be used as objective inputs or contextual measurements.

Analysis must not hard-code a trading stop merely because ATR is present.

---

## 23. Feature Research

Feature research must not stop at simple correlation.

Where scientifically material, Analysis should evaluate:

- association;
- incremental contribution;
- redundancy;
- interaction;
- stability;
- temporal behavior;
- context dependence;
- economic relevance;
- contradiction;
- generalization;
- sample sensitivity.

A feature with weak standalone effect may still be important in interaction.

A redundant feature may still be true but add little incremental value.

A frequently used feature is not automatically scientifically superior.

---

## 24. Feature Classification

Where a campaign requires feature classification, governed categories may include:

```text
CORE_CONTRIBUTOR
CONDITIONAL_CONTRIBUTOR
INTERACTION_ONLY
REDUNDANT
LOW_CONTRIBUTION
UNSTABLE
INSUFFICIENT_EVIDENCE
RETIRED_FOR_CURRENT_CAMPAIGN
```

Classification criteria must be objective, inspectable, and versioned.

Classification is a research result, not permanent deletion from the Tool Library.

---

## 25. Measurement Ranking

Analysis may produce evidence used to rank measurements.

Possible ranking dimensions may include:

- contribution to the research objective;
- incremental information;
- stability;
- redundancy;
- interaction value;
- context specificity;
- false-signal behavior;
- generalization;
- computational/materialization cost as a separate operational dimension.

Usefulness and computational cost must remain separate.

A measurement may be highly useful but expensive.

A measurement may be cheap but uninformative.

A measurement's lack of use is not, by itself, evidence of lack of value.

---

## 26. Deterministic Measurement Convergence Campaign

The permanent Analysis architecture supports, but is not defined by, the Deterministic Measurement Convergence Campaign.

During that campaign:

1. Intake may materialize the complete applicable governed deterministic measurement set.
2. Analysis evaluates those measurements against governed historical research objectives.
3. Analysis characterizes opportunity regions, comparable failures, liquidity traps, and controls.
4. Analysis evaluates contribution, redundancy, interactions, stability, context, contradiction, and other required properties.
5. After each five-ticker cohort, Research Director performs the Measurement Convergence Assessment.
6. Analysis may be asked whether completed research would have materially benefited from tools outside the currently favored set.
7. Successive cohorts continue until governed convergence criteria are met.

The campaign must not permanently shrink Analysis capability.

Lower-ranked deterministic tools remain available in the shared library.

---

## 27. Research Cache

Analysis may create **Research Cache** material during execution.

Research Cache is not a second Research Nexus.

Typical cache material may include:

- temporary joins;
- intermediate matrices;
- temporary cohort tables;
- intermediate model fits;
- exploratory rankings;
- temporary visualizations;
- decompressed working copies;
- scratch statistics;
- candidate result tables;
- repeated-computation acceleration artifacts.

Research Cache is normally Class III transient/replaceable state.

It may be deleted when no longer needed and when deletion does not violate reproducibility, recovery, or scientific-integrity requirements.

---

## 28. Candidate Results vs Durable Findings

Analysis may generate many results while answering one task.

The architecture must distinguish:

### Intermediate / candidate analytical result

A working result that may be useful for interpretation but is not yet required as durable canonical evidence.

Default location:

```text
Research Cache / transient execution state
```

### Governed evidence / finding

A result meeting the task's output criteria or required for:

- Research Director evaluation;
- scientific lineage;
- contradiction preservation;
- reproducibility;
- future reuse;
- audit;
- knowledge-candidate support.

Default location:

```text
Research Nexus
```

Analysis must not publish every intermediate calculation as permanent evidence merely because it was computed.

Likewise, Analysis must not discard material evidence merely because it is inconvenient or contradicts the working hypothesis.

---

## 29. Cache Promotion

Class III Research Cache material may later prove scientifically significant.

Before cache material becomes durable Research Nexus state, it must receive the governed properties required by artifact standards, including as applicable:

- durable identity;
- artifact type;
- schema/version;
- provenance;
- relationship references;
- persistence classification;
- validation;
- retention classification.

Promotion of cached material into durable evidence does not make it knowledge.

---

## 30. Research Director Evaluation of Analysis Output

The Research Director evaluates what the evidence means for research progression.

The Analysis Engine does not decide:

- whether the research question is fully answered;
- whether another question should be asked;
- whether convergence exists for the campaign;
- whether a finding should become a Knowledge Candidate;
- whether a Knowledge Candidate should be promoted.

Analysis may report:

```text
SUPPORTED_BY_THIS_ANALYSIS
NOT_SUPPORTED_BY_THIS_ANALYSIS
CONTRADICTORY_EVIDENCE
INSUFFICIENT_EVIDENCE
MISSING_INPUT
MISSING_CAPABILITY
METHOD_NOT_APPLICABLE
UNSTABLE_RESULT
GENERALIZATION_FAILURE
```

These are bounded analytical outcomes.

They are not global research conclusions unless governance explicitly defines them as such.

---

## 31. Missing Evidence

If required evidence is unavailable, Analysis must say so.

It must not:

- infer absent source data;
- manufacture measurements;
- substitute an unrelated method without disclosure;
- treat task failure as evidence against a hypothesis;
- call insufficient evidence a negative scientific finding.

Possible output:

```text
MISSING_EVIDENCE
required_input: ...
reason: ...
affected_question: ...
valid_alternative_available: true/false
```

Research Director may then determine whether a new governed research need is warranted.

---

## 32. Missing Capability

If MTS lacks a required analytical method, computation, data source, interface, or engine capability, Analysis must report a **Missing Capability** condition.

The report should identify:

```text
missing capability
why required
question/task affected
available alternatives
scientific consequence
```

Analysis must not silently replace a missing method with a materially different one.

---

## 33. Failure Semantics

Execution failure and scientific outcome are separate.

Possible task-execution states include:

```text
SUCCEEDED
FAILED
BLOCKED
CANCELLED
NOT_APPLICABLE
RETRYABLE_FAILURE
```

Possible scientific outcomes include:

```text
SUPPORTED
NOT_SUPPORTED
CONTRADICTED
INSUFFICIENT_EVIDENCE
UNSTABLE
MISSING_CAPABILITY
```

A crashed statistical module is not evidence that a hypothesis is false.

A successful computation is not evidence that a hypothesis is true.

---

## 34. Output Architecture

A completed Analysis task may produce:

- execution record;
- compatibility assessment;
- evidence artifacts;
- finding artifacts;
- method-specific summary artifacts;
- uncertainty/limitation metadata;
- sample-construction record;
- tool/computation-usage record;
- contradiction record;
- missing-evidence report;
- missing-capability report;
- references to transient cache products where required during active work.

Human-readable reports are views of canonical artifacts.

The report must not be the only place where material findings exist.

---

## 35. Finding Content

A material Finding should identify, as applicable:

```text
finding_id
task_ref
research_plan_ref
question_ref
input_artifact_refs
method_id / version
sample definition
result proposition
effect / magnitude
uncertainty
supporting evidence refs
contradictory evidence refs
applicability
limitations
temporal scope
validation state
exploratory / confirmatory status
created_at
producer
```

Exact fields belong in governed schemas/contracts.

---

## 36. Provenance

Every material Analysis output must preserve enough provenance to reproduce and audit it.

Relevant provenance includes:

- input artifact identities/versions;
- Research Plan/version;
- task identity;
- Analysis Engine implementation version;
- method identity/version;
- Deterministic Computation identities/versions;
- configuration;
- parameters;
- random seed where applicable;
- sample-construction logic/version;
- temporal boundaries;
- holdout designation;
- overlap rule;
- transformations;
- output artifact identities.

Physical local cache paths are not scientific identity.

---

## 37. Idempotency and Retry

Where a task and its governed inputs/method/configuration are identical, Analysis should support deterministic or reconcilable retry behavior appropriate to the method.

Deterministic methods should reproduce equivalent canonical scientific content.

Operational telemetry such as:

- elapsed time;
- worker id;
- CPU utilization;
- transient path;
- memory usage;

must not contaminate immutable scientific payload identity unless governance explicitly defines those values as part of the artifact.

Stochastic methods must preserve the random seed and relevant implementation state required for reproducibility.

---

## 38. Concurrency and Scale

The Analysis Engine must be designed for future server execution from the beginning.

It must support:

- multiple concurrent tasks;
- multiple worker processes;
- one or more tasks per CPU resource according to Task Manager policy;
- isolated task-local working state;
- no global mutable singleton research state;
- retry after worker failure;
- independent method execution where safe;
- bounded memory/materialization behavior;
- scalable Nexus retrieval/publication.

Scaling from a laptop to a 16-core, 24-core, or larger server must not require replacing the architecture.

The Task Manager controls scheduling and resource allocation.

Analysis declares capabilities/resource requirements; it does not self-schedule globally.

---

## 39. Worker Model

Analysis may be implemented as a worker pool.

Conceptually:

```text
Task Manager
    ↓
eligible Analysis worker
    ↓
resolve Nexus inputs
    ↓
construct Scientific Execution Context
    ↓
compatibility check
    ↓
materialize required deterministic computations
    ↓
execute bounded analytical method
    ↓
validate result
    ↓
cache intermediates / publish durable outputs
    ↓
return Task Result
```

Workers should be replaceable and stateless with respect to enterprise durable state.

---

## 40. Resource Governance

Analytical methods may declare resource characteristics such as:

- CPU intensity;
- memory intensity;
- expected data size;
- parallelizability;
- accelerator requirements;
- external-library requirements;
- stochastic/deterministic behavior.

Task Manager may use these declarations for scheduling.

Analysis must not hard-code “one engine process = one system task forever.”

---

## 41. Research Nexus Boundary

All durable Analysis state belongs in the Research Nexus.

Analysis must interact through stable Nexus interfaces.

It must not:

- write canonical research artifacts directly into arbitrary filesystem locations;
- depend on SQLite implementation details;
- depend on Nexus payload paths;
- create a parallel warehouse of canonical findings;
- use Research Cache as durable authority.

The Nexus remembers and connects.

Analysis performs work.

---

## 42. Relationships

Where material, published Analysis artifacts should preserve governed relationships such as:

```text
finding
  → produced_by → Analysis execution

finding
  → evaluates → Research Question / hypothesis

finding
  → derived_from → input dataset

finding
  → uses → method/version

finding
  → uses → deterministic computation/version

finding
  → supports / contradicts → proposition

finding
  → belongs_to → Research Plan / campaign
```

Relationship semantics belong in Nexus governance/contracts.

---

## 43. Authority Boundary

Analysis may:

- read authorized governed inputs;
- execute admitted analytical work;
- invoke approved shared deterministic tools;
- use approved analysis methods;
- create task-local cache;
- publish authorized evidence/findings;
- report missing evidence/capability.

Analysis may not, solely by its own authority:

- create unrestricted Research Plans;
- pass Research Admission;
- change governance;
- widen its permissions;
- schedule arbitrary workers;
- declare knowledge canonical;
- pass Knowledge Promotion;
- create investment Decisions;
- submit trades;
- privately acquire source data;
- erase contradictory canonical evidence.

---

## 44. Relationship to Research Director

Research Director owns:

- question formation;
- hypothesis formation;
- research progression;
- Research Plan authorship;
- interpretation across multiple findings;
- follow-up questioning;
- convergence assessment;
- Knowledge Candidate authorship where permitted.

Analysis owns:

- bounded empirical execution;
- method compatibility;
- measurement/materialization within task authority;
- evidence generation;
- finding generation;
- uncertainty/limitation reporting;
- missing-capability reporting.

This boundary must remain explicit even if both components eventually use AI internally.

---

## 45. Relationship to Data Intake

Data Intake owns:

- external acquisition;
- source validation;
- canonical normalization;
- routine/broad deterministic materialization;
- intake provenance;
- canonical market-history publication.

Analysis may consume Intake-produced data only through governed Nexus interfaces.

Analysis may compute additional deterministic measurements from valid existing inputs.

Analysis must route unavailable source-data needs through the governed research/task path to Data Intake.

---

## 46. Relationship to Accountability

Accountability independently evaluates required research gates.

Analysis does not pass Research Admission.

Analysis does not pass Knowledge Promotion.

Analysis may produce evidence required by Accountability criteria.

Accountability must not rewrite Analysis's scientific output merely to make a case pass.

---

## 47. Relationship to Decision

Decision consumes governed knowledge/current state under its own authority.

Analysis does not make trade decisions merely because it discovers an economically interesting relationship.

Analysis outputs may eventually contribute to governed knowledge that Decision can use after required validation/promotion.

Research findings and investment decisions remain distinct artifact classes.

---

## 48. Relationship to Learning & Governance

Learning & Governance may later evaluate:

- method effectiveness;
- measurement usefulness;
- computational cost;
- outcome relevance;
- false-discovery patterns;
- tool ranking;
- research-process performance.

Analysis may expose usage/provenance data needed for those evaluations.

Learning/usage ranking must not silently rewrite scientific validity.

---

## 49. Initial v2 Analysis Capability Set

The first implementation should be intentionally small but architecturally complete.

Recommended first executable capabilities:

1. dataset introspection;
2. descriptive statistics;
3. cohort/outcome comparison;
4. relationship/redundancy analysis;
5. basic statistical reliability;
6. shared deterministic computation invocation;
7. future-price geometry for explicitly retrospective research;
8. sample/overlap/temporal-context preservation;
9. transient Research Cache;
10. governed Finding publication to Nexus.

This is enough to prove the architecture without recreating the full legacy method surface immediately.

---

## 50. First Vertical Slice

The first Analysis vertical slice should use a real Intake-published market-history artifact.

Preferred path:

```text
raw historical ticker
    ↓
Intake
    ↓
Research Nexus — NORMALIZED_DATASET
    ↓
governed Analysis task
    ↓
Analysis resolves dataset
    ↓
Scientific Execution Context
    ↓
Foundation / Descriptive / Comparison
    ↓
additional deterministic computation if required
    ↓
Finding
    ↓
Research Nexus
    ↓
retrieve + verify + retry
```

The proof should demonstrate:

- no private Intake → Analysis handoff;
- no filesystem dependency on Intake output;
- Nexus-only durable input/output;
- reproducible sample construction;
- temporal integrity;
- analytical method/version provenance;
- deterministic computation independence from Intake materialization;
- cache/durable-output separation;
- canonical Finding retrieval;
- idempotent/reconcilable retry;
- explicit failure behavior.

---

## 51. First Research Experiment

After the minimum vertical slice is proven, the Deterministic Measurement Convergence Campaign may become the first substantial workload.

For each selected ticker/cohort, governed research may evaluate which deterministic measurements are associated with and contribute to defined historical outcome regions.

The experiment should include:

```text
proximal opportunity regions
vs.
comparable failures / controls / liquidity traps
```

and evaluate measurements for:

- contribution;
- redundancy;
- interaction;
- stability;
- context dependence;
- false-signal behavior;
- generalization.

After each five-ticker cohort, Research Director—not Analysis—performs the governed convergence assessment.

---

## 52. Hypothesis Neutrality

Analysis must not encode favored hypotheses as architectural truth.

For example, the system may test:

```text
SMA 20 > SMA 50 > SMA 200
+
increasing volume
+
relatively stable price
```

as a research hypothesis.

The Analysis Engine architecture must not assume that hypothesis is correct.

The engine must be equally capable of finding:

- strong support;
- conditional support;
- redundancy;
- contradiction;
- regime dependence;
- failure;
- no meaningful contribution.

Architecture exists to make the evidence answer the question.

---

## 53. Legacy v1 Lessons

Legacy Engine 09 is a source of lessons, not a software dependency.

Useful concepts worth preserving conceptually include:

- modular analytical capability;
- compatibility checks;
- explicit method identifiers;
- descriptive analysis;
- comparison;
- statistical evaluation;
- predictive validation;
- incremental contribution;
- robustness;
- relationship/redundancy;
- economic analysis;
- contradiction;
- generalization;
- exploratory relationship/conditional/interaction/context/anomaly discovery.

The v2 implementation must not automatically preserve:

- legacy directory structure;
- legacy import paths;
- legacy warehouse coupling;
- legacy dataset-loader assumptions;
- legacy engine numbering;
- legacy module orchestration;
- legacy schemas;
- legacy output formats;
- legacy method dependencies;
- legacy feature limitations;
- legacy ownership boundaries.

Every concept must earn its place under v2 architecture/governance.

---

## 54. Architectural Correction from v1

The key permanent corrections are:

### Analysis is not limited by Intake output

Shared deterministic computation is system capability.

### Analysis does not own research progression

Research Director does.

### Analysis does not own scheduling

Task Manager does.

### Analysis does not own durable storage

Research Nexus does.

### Intermediate results do not automatically become permanent findings

Research Cache and durable Nexus evidence are distinct.

### Successful computation is not successful science

Scientific meaning requires governed evaluation.

### Future outcome information must remain separated from contemporaneous inputs

Historical visibility is useful for evaluation, not permission for leakage.

---

## 55. Testing Strategy

### Unit tests

Validate:

- method calculations;
- compatibility logic;
- sample construction;
- overlap rules;
- future-information separation;
- deterministic computation invocation;
- cache behavior;
- output validation.

### Contract tests

Validate:

- governed task input;
- Nexus artifact schemas;
- Finding schema;
- provenance requirements;
- controlled vocabulary;
- authority boundaries.

### Integration tests

Validate:

- Task Manager → Analysis;
- Analysis → Research Nexus;
- Analysis retrieval from Nexus;
- shared deterministic library invocation;
- cache promotion/retirement where applicable.

### End-to-end tests

Validate real multi-component paths from Intake-published data to Analysis finding retrieval.

### Scientific regression tests

Validate known synthetic datasets where expected statistical relationships, null relationships, leakage conditions, overlap effects, and contradictions are controlled.

### Failure/recovery tests

Validate:

- retry;
- interrupted execution;
- missing input;
- incompatible method;
- stale/invalid reference;
- partial cache;
- worker restart;
- conflicting immutable publication.

---

## 56. Conformance Requirements

The Analysis Engine conforms to this architecture only if it:

1. performs bounded empirical work;
2. consumes governed tasks rather than inventing unrestricted work;
3. resolves durable inputs through Research Nexus;
4. does not depend on Intake private storage;
5. retains access to the shared Deterministic Computation Library;
6. is not limited to Intake-materialized measurements;
7. separates deterministic computation from analytical interpretation;
8. preserves temporal/future-information integrity;
9. preserves sample construction and overlap policy;
10. distinguishes exploratory from confirmatory work;
11. preserves method/version/configuration provenance;
12. supports objective uncertainty/limitation reporting;
13. supports missing evidence and missing capability;
14. distinguishes execution failure from scientific outcome;
15. uses transient Research Cache for replaceable working material;
16. publishes material durable evidence/findings through Research Nexus;
17. does not treat every intermediate result as permanent evidence;
18. does not self-promote findings to knowledge;
19. does not schedule global work;
20. does not privately acquire external source data;
21. does not make investment Decisions;
22. supports retry/recovery;
23. supports concurrency without singleton assumptions;
24. can scale to mature server deployment without architectural replacement;
25. remains replaceable behind stable task/Nexus contracts.

---

## 57. Architectural Decision

The Analysis Engine is deliberately **analytically powerful but authority-limited**.

Its permanent design centers on:

- bounded scientific execution;
- methodological extensibility;
- shared access to deterministic computation;
- freedom from Intake-materialization limits;
- explicit temporal integrity;
- reproducible sample construction;
- evidence rather than narrative;
- transient Research Cache for working products;
- selective durable publication;
- Nexus-only durable state;
- Research Director ownership of research progression;
- Accountability ownership of independent gates;
- Task Manager ownership of scheduling;
- server-scale concurrency without architectural replacement.

The engine should become broader and more capable over time without becoming the hidden center of MTS.

> **Analysis may use many tools, create new valid methods, and perform substantial scientific work. It remains a bounded evidence-producing engine.**
