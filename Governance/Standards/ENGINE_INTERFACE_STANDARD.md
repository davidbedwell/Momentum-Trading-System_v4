# Momentum Trading System — Engine Interface Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, `ARTIFACT_GOVERNANCE_STANDARD.md`, `SCHEMA_STANDARD.md`, and `STORAGE_RETENTION_STANDARD.md`.

---

## 1. Purpose

This standard defines how MTS engines participate in the system.

It governs:

- engine identity;
- capability declaration;
- task acceptance;
- input/output contracts;
- Research Nexus interaction;
- Task Manager interaction;
- execution records;
- failure semantics;
- concurrency;
- idempotency;
- observability;
- authority boundaries;
- future engine addition and replacement.

The purpose is to make engines independently replaceable components that perform bounded work without owning system-wide coordination, canonical storage, or authority outside their declared role.

---

## 2. Governing Principle

> **An engine is a capability provider, not a private subsystem.**

An engine receives governed work, consumes governed inputs, performs its authorized function, and returns governed results.

It must not require other components to understand its private filesystem layout or internal implementation.

---

## 3. Design With the End in Mind

Engine interfaces must be designed for the mature MTS architecture from the beginning.

The same logical interface must support evolution from:

```text
single Mac
single process
one worker
sequential execution
```

to:

```text
server deployment
multiple processes
multiple workers
concurrent execution
remote services where useful
live-market workloads
```

Concurrency and distribution may be deferred operationally.

Interface redesign for concurrency must not be required later.

---

## 4. Functional Engine Identity

Canonical engines are identified by function rather than historical number.

Initial functional identities include:

```text
engine:data-intake
engine:discovery
engine:research-director
engine:market-discovery
engine:decision
engine:learning-governance
```

Additional engines may be added through governance.


---

## 5. Engine vs Worker

An engine is a logical capability domain.

A worker is a runtime execution instance.

Example:

```text
engine_id: engine:discovery
worker_id: worker:01J...
```

Multiple workers may execute tasks for one engine.

A worker must not be treated as the durable identity of the engine.

---

## 6. Capability Declaration

Each engine must declare machine-readable capabilities.

A capability declaration should identify:

```text
engine_id
capabilities
accepted_task_types
accepted_input_schema_versions
produced_artifact_types
produced_schema_versions
resource characteristics where material
interface_version
```

The Task Manager uses capability information to route work.

Routing must not depend solely on hard-coded engine names.

---

## 7. Engine Registration

Runtime workers must register or otherwise become discoverable to the Task Manager.

Registration may include:

```text
worker_id
engine_id
capabilities
software_version
interface_version
status
resource availability
started_at
heartbeat/lease information
```

Registration is operational state.

Material execution provenance may preserve relevant registration/version information in the Research Nexus.

---

## 8. Engine Authority

Capability and authority are different.

An engine may technically be capable of constructing an artifact but may publish only artifact families authorized by governance.

Examples:

- Data Intake does not make investment decisions.
- Discovery does not execute trades.
- Research Director does not silently become the scheduler or its own independent research gatekeeper.
- Decision does not rewrite research evidence.
- Learning & Governance does not retroactively alter historical Decision context.

Authority boundaries must be enforced at interfaces, not merely documented.

---

## 9. Task Manager Boundary

The Task Manager owns system-wide work coordination.

It is responsible for functions such as:

- accepting governed Task Requests;
- dependency tracking;
- routing by capability;
- scheduling;
- priority;
- retry policy;
- worker assignment;
- timeout handling;
- task state;
- recovery after interruption;
- concurrency control.

Engines do not create private competing task-coordination systems.

---

## 10. Research Director Boundary

The Research Director determines what research is needed.

It may:

- formulate questions;
- create research plans;
- identify missing evidence;
- request additional research;
- evaluate whether research has converged sufficiently;
- create governed Task Requests/research needs.

It does not directly own worker scheduling.

Research intent flows to the Task Manager as governed work.

---


## 11. Accountability Boundary

The Accountability Engine consumes governed proposals/candidates, applicable
policy, and required evidence through stable interfaces.

It produces governed gate verdicts for:

```text
RESEARCH_ADMISSION
KNOWLEDGE_PROMOTION
```

The interface must not give Accountability direct authority to schedule workers,
mutate another engine's private state, or approve individual trades.

Research Director must submit proposed Research Plans and Knowledge Candidates
through governed Accountability interfaces when policy requires those gates.

Task Manager must be able to verify required Research Admission status without
depending on Accountability's private filesystem or process memory.

## 12. MTS Control Interface Boundary

The `mts` control interface may initiate governed work.

Conceptually:

```text
Human / Automation
       ↓
mts / UI / API
       ↓
Task Manager
       ↓
Engine worker
```

The control interface does not bypass engine contracts or acquire engine authority.

---

## 13. Task Request

Engines must receive governed Task Requests rather than undocumented positional command sequences for material work.

A Task Request should identify:

```text
task_id
task_type
requested_capability
input_refs
dependencies
priority
requester
policy/context refs
schema/version
```

Exact structure belongs in Governance/Schemas.

---

## 14. Input by Reference

Durable engine inputs should normally be referenced by governed identity.

Example:

```text
input_refs:
  - artifact:...
  - artifact:...
```

The engine resolves required representations through governed Research Nexus interfaces.

This prevents Task Requests from becoming giant duplicated payloads and prevents physical path coupling.

---

## 15. Small Inline Inputs

Small immutable parameters may be included directly in a Task Request when governed by schema.

Examples:

```text
date range
requested horizon
research parameter
mode
limit
```

Inline values must not become a way to bypass provenance for material scientific inputs.

---

## 16. Input Validation

Before scientific execution, an engine must validate that:

- the task type is supported;
- required inputs exist;
- schema versions are supported;
- required capabilities/data are present;
- policy permits the operation;
- input lifecycle/status is acceptable where relevant.

Invalid input must fail explicitly.

---

## 17. Output Publication

Material outputs must be published through governed Research Nexus interfaces.

Publication must enforce:

- identity;
- schema;
- provenance;
- artifact authorization;
- lifecycle;
- persistence metadata;
- duplicate/collision behavior.

An engine must not treat “file written successfully” as equivalent to “artifact published successfully.”

---

## 18. Output by Reference

Task completion should return governed output references rather than making downstream components scrape directories.

Example:

```text
output_refs:
  - finding:...
  - dataset:...
```

Human-readable reports may additionally be produced as views.

---

## 19. Task Execution State vs Semantic Result

Task-execution state and scientific/business result are distinct.

Task execution may be:

```text
SUCCEEDED
FAILED_RETRYABLE
FAILED_TERMINAL
CANCELLED
TIMED_OUT
BLOCKED_DEPENDENCY
```

A successful task may produce a semantic result such as:

```text
INSUFFICIENT_EVIDENCE
MISSING_CAPABILITY
NO_ACTION
RESEARCH_REQUIRED
```

A legitimate semantic result must not be mislabeled as a software failure.

A software failure must not masquerade as a legitimate semantic result.

---

## 20. Explicit Failure

Engines must fail explicitly.

They must not:

- silently skip required inputs;
- silently substitute another dataset;
- silently write to fallback storage;
- silently change schema;
- fabricate a conclusion after a missing capability;
- convert exceptions into successful empty results without governed meaning.

---

## 21. Retryability

Failures must indicate whether retry is meaningful.

Examples of potentially retryable conditions:

- temporary storage unavailability;
- transient provider failure;
- worker interruption;
- temporary resource exhaustion.

Examples of normally terminal conditions:

- invalid schema;
- unsupported task type;
- impossible parameter;
- policy violation;
- corrupted required input.

Exact classification belongs in task governance.

---

## 22. Idempotency

Material engine tasks should be designed for safe retry.

A repeated execution of the same task must not create uncontrolled duplicate durable artifacts.

Where outputs are deterministic and already published, retry may return existing references.

Where a new execution legitimately creates a new version or occurrence, that distinction must be explicit.

---

## 23. Execution Identity

Every material attempt receives a distinct `execution_id`.

Retries preserve:

```text
same task_id
different execution_id
```

Execution records must not erase prior failed attempts.

---

## 24. Provenance

Every material output must identify its producing execution.

Execution provenance should support:

```text
task_ref
execution_id
engine_id
worker_id
software_version
model_version where applicable
configuration refs
input refs
output refs
timestamps
```

---

## 25. Software Version

Material execution records must identify the software version sufficiently to support reproducibility and debugging.

A Git commit hash may be included for source-controlled implementations.

Uncommitted local modifications, when permitted in development, should be detectable in execution provenance.

Production-like scientific publication should normally use identifiable source state.

---

## 26. Configuration

Engines must receive configuration through governed configuration mechanisms.

They must not depend on:

- developer-specific absolute paths;
- hidden local constants;
- manually edited source code for ordinary deployment changes.

Scientific parameters that materially affect results must be preserved in provenance.

---

## 27. Storage Independence

Engines must not own Research Nexus physical paths.

They should interact through:

- Nexus APIs/services;
- governed SDKs;
- logical storage roles where direct access is explicitly authorized.

Moving the Nexus to different hardware must not require rewriting engine scientific logic.

---

## 28. Private Working Storage

An engine may use private Class III working storage for:

- scratch;
- temporary decompression;
- intermediate calculations;
- worker-local cache.

Private working storage is not canonical publication.

Any scientifically significant result that must survive must be published into governed Class II state.

---

## 29. No Cross-Engine Private Filesystem Contract

One engine must not require another engine to read its private working directory.

Cross-engine communication occurs through:

- Task Manager work state;
- Research Nexus artifacts;
- governed messaging/interfaces.

This prevents hidden coupling.

---

## 30. Concurrency

Engine interfaces must assume that multiple tasks may eventually execute concurrently.

Therefore implementations must avoid reliance on:

- one global mutable current task;
- one fixed output filename;
- one shared unprotected scratch directory;
- process-wide mutable scientific state;
- implicit sequential ordering.

Concurrency safety is part of interface correctness.

---

## 31. Resource Awareness

Tasks may declare or estimate resource needs where useful.

Examples:

```text
CPU
memory
storage
provider quota
GPU
network
exclusive resource
```

The Task Manager may use these for scheduling.

An engine must not assume unlimited resources.

---

## 32. Cancellation

Long-running tasks should support governed cancellation where practical.

Cancellation must:

- stop safely;
- preserve diagnostics;
- not publish incomplete output as complete;
- record execution state;
- clean or mark temporary state appropriately.

---

## 33. Timeout

Tasks subject to timeout must distinguish timeout from scientific insufficiency.

A timed-out analysis is not evidence that no relationship exists.

---

## 34. Progress

Long-running engines may emit structured progress/heartbeat information.

Progress is operational information and must not be confused with scientific output.

Progress reporting should not require polling private engine files.

---

## 35. Heartbeats and Leases

Server-scale workers may use heartbeat/lease mechanisms so the Task Manager can detect lost workers.

A lost heartbeat may cause an execution to become recoverable/retryable according to policy.

Heartbeat state is normally Class III operational state unless materialized into durable execution history.

---

## 36. Observability

Engines must emit sufficient structured diagnostics to support:

- execution tracing;
- failure diagnosis;
- performance analysis;
- resource monitoring;
- task correlation.

Logs should include governed identifiers such as:

```text
task_id
execution_id
engine_id
worker_id
```

Important scientific facts must not exist only in logs.

---

## 37. Metrics

Operational metrics may include:

- task duration;
- queue-to-start latency;
- success/failure counts;
- retry count;
- memory/CPU use;
- artifact publication count;
- provider latency.

Metrics do not replace execution records.

---

## 38. Determinism

Where an engine operation is expected to be deterministic, repeated execution with the same:

- input versions;
- configuration;
- code/model version;

should produce equivalent results.

Where nondeterminism is intentional, its source should be controlled or recorded when material.

---

## 39. Randomness

Scientific engines using randomness should record:

- seed where applicable;
- algorithm/model version;
- relevant stochastic configuration.

This supports reproducibility.

---

## 40. Data Intake Interface

Data Intake should accept governed acquisition/intake work and produce governed data artifacts and QA results.

It must not:

- interpret data as an investment recommendation;
- silently overwrite source data;
- publish failed QA as accepted data.

---

## 41. Discovery Interface

Discovery should accept governed discovery/measurement work and produce observations, measurements, evidence, and findings within its authority.

Discovery may proactively search for patterns when tasked to do so.

It must distinguish measurement from interpretation and action.

---

## 42. Research Director Interface

Research Director should consume the State of Knowledge and research context, then produce governed research intent such as:

- questions;
- hypotheses;
- research plans;
- research needs;
- requests for additional evidence;
- convergence/insufficiency results.

It must not implement private scheduling logic that bypasses the Task Manager.

---

## 43. Market Discovery Interface

Market Discovery should search current/live market state for conditions, patterns, candidates, and opportunities within its governed scope.

It may request research when an observed pattern lacks adequate knowledge.

It does not make the final investment decision merely because it found a candidate.

---

## 44. Decision Interface

Decision consumes governed current state, SoK/knowledge, market context, portfolio/risk context, and policy.

It produces governed Decision artifacts.

Decision task success is distinct from a semantic `NO_ACTION`.

---

## 45. Learning & Governance Interface

Learning & Governance consumes decisions, outcomes, evidence, and performance history.

It may produce:

- evaluations;
- ranking inputs;
- lifecycle recommendations;
- policy/model recommendations;
- drift/instability findings.

It must not silently rewrite prior decisions or evidence.

---

## 46. Engine-to-Engine Requests

An engine should not directly command another worker outside governed coordination.

If Discovery determines Data Intake work is required, or Research Director needs additional analysis, it creates or causes creation of governed work for the Task Manager.

This preserves:

- priority;
- dependency tracking;
- auditability;
- concurrency control;
- recovery.

---

## 47. Capability Gaps

When an engine cannot complete a scientifically valid task because a required capability is absent, it should return a governed `MISSING_CAPABILITY` semantic result and, where authorized, create/reference a `RESEARCH_NEED` or capability need.

It must then release the task according to Task Manager rules rather than blocking indefinitely.

---

## 48. Insufficient Evidence

When execution succeeds but available evidence cannot answer the scientific question, the engine should return `INSUFFICIENT_EVIDENCE` or the appropriate governed semantic result.

This is not `FAILED_TERMINAL`.

---

## 49. Interface Versioning

Cross-component engine interfaces must have explicit versions.

Breaking interface changes require:

- new interface version;
- affected producer/consumer analysis;
- compatibility plan;
- tests.

Engine implementation versions and interface versions are distinct.

---

## 50. Backward Compatibility

During migration, the system may support more than one interface version.

Compatibility adapters must be explicit and temporary/governed.

Compatibility code must not become an undocumented permanent alternate architecture.

---

## 51. Engine Replacement

A compliant engine implementation should be replaceable if the replacement:

- registers the same governed capability;
- accepts the required interface/schema versions;
- preserves authority boundaries;
- produces compliant artifacts;
- passes conformance tests.

Other engines should not require redesign solely because the implementation changed.

---

## 52. New Engine Addition

Adding a future engine should require:

1. defining its responsibility;
2. defining capability identifiers;
3. defining accepted task types;
4. defining input/output contracts;
5. defining artifact authority;
6. registering it with the Task Manager;
7. passing conformance tests.

It should not require redesigning the Research Nexus.

---

## 53. Security and Least Authority

Engines should receive only the permissions required for their function.

Examples:

- read-only access where publication is unnecessary;
- publication authority limited by artifact type;
- no direct deletion authority unless explicitly governed;
- secrets provided through governed configuration.

A compromised or defective engine should not automatically have unrestricted Nexus authority.

---

## 54. Testability

Every engine interface must support isolated testing.

Tests should be able to provide:

- synthetic Task Requests;
- isolated Nexus/test stores;
- controlled configuration;
- deterministic fixtures;
- mocked/fake external providers where appropriate.

Tests must not require production data or production storage.

---

## 55. Contract Tests

Each engine must pass contract tests verifying at least:

- capability declaration;
- supported task validation;
- unsupported task rejection;
- input schema validation;
- output schema validation;
- authorized publication;
- explicit failure behavior;
- task/execution identity separation;
- idempotent retry behavior where applicable;
- storage independence;
- isolated test operation.

---

## 56. Integration Tests

Integration tests should verify:

```text
Task Manager
→ engine worker
→ Research Nexus
→ output references
→ downstream dependency release
```

without relying on private filesystem coupling.

---

## 57. End-to-End Tests

Representative end-to-end tests should prove that governed work can move through multiple engines while preserving:

- identity;
- provenance;
- schemas;
- task dependencies;
- failure semantics;
- scientific boundaries.

---

## 58. Initial v2 Implementation

The initial engine interface layer should provide:

- common engine registration structure;
- capability declaration;
- common Task Request/Execution structures;
- common result envelope;
- Research Nexus client boundary;
- Task Manager worker boundary;
- structured diagnostics;
- conformance test harness.

The first implementation may run all workers locally.

Its contracts must remain valid when workers later run on the server.

---

## 59. Prohibited Practices

The following are prohibited:

- hard-coded cross-engine filesystem reads;
- engine-number-based routing as the canonical mechanism;
- private scheduler loops competing with Task Manager;
- silent output publication;
- ungoverned artifact writes;
- conflating task failure with scientific result;
- one global mutable “current task” assumption;
- fixed shared output filenames;
- engine-specific durable ID schemes;
- hidden fallback storage;
- downstream parsing of another engine's console output as an interface.

---

## 60. Conformance

An engine conforms when it:

1. has functional identity and declared capabilities;
2. accepts governed Task Requests;
3. validates inputs;
4. uses governed identities and schemas;
5. publishes only authorized artifact types;
6. publishes through governed Nexus interfaces;
7. separates task execution state from semantic result;
8. records material execution provenance;
9. supports safe retry/idempotency where required;
10. avoids physical storage coupling;
11. avoids private cross-engine filesystem contracts;
12. remains compatible with future concurrent execution;
13. exposes sufficient diagnostics;
14. passes contract tests.

---

## 61. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/TASK_MANAGEMENT_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md

Governance/Contracts/
Governance/Schemas/
```

---

## 62. Closing Principle

MTS must always be able to replace:

- a worker;
- an engine implementation;
- a storage backend;
- a machine;

without changing the scientific meaning of the work exchanged between components.

If another component must know an engine's private directories, internal classes, or implementation tricks to use its output, the interface is not sufficiently governed.
