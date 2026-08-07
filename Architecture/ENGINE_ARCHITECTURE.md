# Momentum Trading System — Engine Architecture

**Status:** Canonical
**Authority:** Governing engine architecture subordinate to `CHARTER.md`, `Architecture/SYSTEM_ARCHITECTURE.md`, and `Architecture/RESEARCH_NEXUS_ARCHITECTURE.md`

---

## 1. Purpose

This document defines the enduring architecture of MTS engines and the permanent boundaries among engines, the Task Manager, the Research Nexus, and shared core services.

It establishes:

- what an engine is;
- what an engine may own;
- how engines declare capabilities;
- how work reaches engines;
- how engines publish results;
- how engines scale;
- how failures are isolated;
- how authority is separated;
- how new engines are added without redesigning existing ones.

This document intentionally avoids prescribing specific classes, frameworks, queues, process managers, RPC technologies, container systems, or deployment tools. Those belong in technical design.

---

## 2. Governing Principle

> **Engines perform bounded work. The Task Manager schedules, routes, and supervises work. The Research Nexus preserves and connects durable state. Governance defines authority and contracts.**

An engine is not the system.

No engine may become the hidden center of MTS by owning permanent storage, global scheduling, project-wide policy, or another engine's implementation details.

---

## 3. Design With the End in Mind

MTS engine architecture SHALL be designed for the known mature operating model from the beginning.

The architecture must support:

- server deployment;
- concurrent execution;
- multiple workers per capability;
- scheduled and autonomous intake;
- iterative autonomous research;
- live-market workloads;
- worker pools;
- retries;
- task recovery;
- capability-based routing;
- horizontal scaling;
- independent engine evolution;
- future engines not presently envisioned.

An initial engine implementation MAY execute as a single local process on one computer.

The engine contract SHALL nevertheless remain suitable for the mature server-scale system.

The governing design test is:

> **Would this engine boundary still make sense if MTS were running concurrently on a multi-core server today?**

If not, the boundary must be reconsidered before implementation.

---

## 4. Definition of an Engine

An engine is a bounded MTS computational component with:

- a defined scientific or operational responsibility;
- declared capabilities;
- governed inputs;
- governed outputs;
- explicit authority boundaries;
- explicit failure semantics;
- observable execution;
- no ownership of enterprise durable state;
- no dependence on private internals of another engine.

An engine may be implemented by one process, many workers, or a distributed service without changing its logical identity.

---

## 5. Engine Identity vs Worker Identity

MTS distinguishes an **engine** from a **worker**.

### Engine

A logical capability domain.

Examples:

- Data Intake Engine;
- Discovery Engine;
- Research Director;
- Accountability Engine;
- Market Discovery Engine;
- Decision Engine;
- Learning & Governance.

### Worker

A runtime execution unit capable of performing one or more engine capabilities.

One engine may have many workers.

A worker must have its own runtime identity for:

- execution tracking;
- failure isolation;
- resource accounting;
- provenance;
- observability.

A worker identity does not create a new engine identity.

---

## 6. Capability-Based Architecture

Work is routed by declared capability rather than hard-coded engine paths or module names.

Each engine exposes a governed capability set.

Illustrative capabilities may include:

```text
INGEST_MARKET_DATA
NORMALIZE_DATASET
VALIDATE_DATASET
GENERATE_MEASUREMENTS
DISCOVER_RELATIONSHIPS
TEST_INTERACTIONS
TEST_TEMPORAL_EFFECTS
RESEARCH_QUESTION
BUILD_RESEARCH_PLAN
EVALUATE_FINDINGS
SCAN_LIVE_MARKET
EVALUATE_DECISION
EVALUATE_KNOWLEDGE_OUTCOME
REVIEW_LIFECYCLE
```

The exact capability vocabulary belongs in governance and may evolve.

The Task Manager routes a task to a worker whose declared capabilities satisfy the task requirements.

This allows MTS to add or replace engine implementations without embedding implementation-specific routing logic into research or decision components.

---

## 7. Engine Registration

Each engine or worker must register enough information for the Task Manager to route work safely.

Registration should include, as applicable:

- engine identity;
- worker identity;
- supported capabilities;
- implementation version;
- supported contract versions;
- supported schema versions;
- resource requirements;
- concurrency capacity;
- availability state;
- optional hardware characteristics;
- optional provider dependencies.

Registration is operational state.

Durable records of significant execution versions may be preserved in the Research Nexus as provenance.

Worker heartbeats, local availability caches, and reconstructable queue
state are normally Class III. Governed Task Requests, dependency state,
and execution records required for restart recovery or provenance are
Class II Research Nexus artifacts.

---

## 8. Task Intake

Engines do not discover arbitrary work by scanning another engine's private folders.

Work reaches an engine through governed task contracts coordinated by the Task Manager.

A task should identify, as applicable:

```text
task_id
task_type
required_capability
priority
input_refs
dependency_refs
policy_refs
requested_by
created_at
deadline_or_freshness
resource_requirements
retry_policy
expected_output_contract
```

Exact fields belong in schemas and contracts.

Tasks may be created by:

- the Research Director;
- the Decision Engine;
- Market Discovery;
- Learning & Governance;
- Data Intake workflows;
- scheduled system operations;
- a human operator;
- other authorized future components.

---

## 9. Task Manager Boundary

The Task Manager is the permanent MTS coordination authority.

It determines:

- when work executes;
- where work executes;
- which eligible worker executes it;
- whether dependencies are ready;
- how many workers may execute concurrently;
- how retries are handled;
- how interruptions are recovered;
- how resource limits are enforced.

The Task Manager does **not** determine:

- what a finding means;
- what research conclusion should be reached;
- whether knowledge should be believed;
- whether a trade should be taken;
- how an engine implements its scientific method.

Scientific components decide what scientific work is needed.

Decision components decide what decision work is needed.

The Task Manager makes the work happen.

---

## 10. Research Nexus Boundary

Engines consume and publish durable artifacts through governed Research Nexus interfaces.

No engine owns permanent enterprise state.

An engine may maintain temporary Class III state while executing.

Any result that must survive process termination, be reused, be audited, be reproduced, or be consumed as durable system state must be published to the Research Nexus according to policy.

Examples include:

- accepted data;
- evidence;
- findings;
- research plans;
- knowledge proposals;
- decisions;
- outcomes;
- lifecycle evaluations;
- material execution provenance.

---

## 11. Engine-Private Storage

Engine-private storage is permitted only for temporary operational use.

Examples:

- local scratch;
- transient working files;
- in-memory state;
- temporary materializations;
- temporary checkpoints where policy permits.

Engine-private state may not become the canonical system of record.

If engine-private state becomes scientifically or operationally significant, it must be classified and published to the Research Nexus before it is treated as durable.

---

## 12. Input and Output Contracts

Every engine boundary must be governed by explicit contracts.

Contracts define:

- required input semantics;
- accepted schemas;
- required metadata;
- expected output semantics;
- error states;
- version compatibility;
- provenance requirements;
- validation responsibilities.

An engine may change its internal implementation without affecting other engines when its governed contracts remain compatible.

Point-to-point undocumented assumptions are prohibited.

---

## 13. Schema Compatibility

Engines must declare which durable schema versions they can consume and produce.

Breaking schema changes require governed migration or compatibility handling.

No engine may silently reinterpret the meaning of an existing field.

Schema validity establishes structural compatibility, not scientific validity.

---

## 14. Engine Authority Model

Authority is explicit and bounded.

### Data Intake Engine

May:

- acquire data;
- normalize data;
- validate data;
- generate deterministic measurements;
- publish governed datasets and validation records.

May not:

- declare economic meaning;
- promote findings to knowledge;
- make investment decisions.

### Discovery Engine

May:

- analyze governed data;
- produce evidence;
- produce findings;
- characterize uncertainty;
- identify contradiction;
- test relationships and interactions.

May not:

- unilaterally promote its own findings to canonical knowledge;
- make investment decisions;
- alter research policy.

### Research Director

May:

- inspect State of Knowledge and Active Research State;
- formulate research questions;
- create proposed Research Plans;
- respond to Accountability gate outcomes;
- request additional intake or analysis after Research Admission;
- evaluate returned findings;
- generate follow-up research;
- publish research conclusions;
- propose Knowledge Candidates.

May not:

- admit its own Research Plan across the independent Research Admission gate;
- promote its own Knowledge Candidate across the independent Knowledge Promotion gate;
- make investment decisions merely because it understands research;
- bypass the Task Manager for scheduled work;
- own persistent research state outside the Nexus.

### Accountability Engine

May:

- evaluate proposed Research Plans against the Research Admission policy;
- evaluate Knowledge Candidates against Knowledge Promotion policy;
- inspect required evidence, provenance, validation, resource, duplication,
  Charter-alignment, applicability, and contradiction state;
- issue governed gate verdicts;
- require revision, narrower scope, more research, or explicit unresolved state
  when objective gate criteria are not satisfied.

May not:

- formulate the scientific conclusion it is evaluating;
- create research merely to justify its own verdict;
- schedule workers;
- alter gate criteria or policy;
- own canonical knowledge;
- make investment decisions;
- approve or reject an individual trade;
- expand its own authority.

### Market Discovery Engine

May:

- inspect current/live market state;
- detect known opportunity patterns;
- surface anomalies;
- identify novel phenomena;
- create candidate opportunities;
- create research-worthy observations.

May not:

- make final trade decisions unless separately granted a Decision capability by architecture;
- silently convert novelty into knowledge.

### Decision Engine

May:

- consume applicable SoK and current state;
- evaluate actionable opportunities;
- determine enter/do-not-enter;
- determine long/short;
- select instruments;
- determine position sizing and scalability;
- manage risk and exits according to governed decision policy;
- create Research Needs when knowledge is insufficient.

May not:

- silently perform scientific research;
- rewrite canonical knowledge;
- bypass governed risk policy.

### Learning & Governance

May, according to policy:

- evaluate knowledge usefulness;
- evaluate decision outcomes;
- identify degradation;
- identify contradiction;
- recommend or execute lifecycle transitions;
- evaluate promotion criteria;
- evaluate supersession and retirement eligibility.

May not:

- alter historical evidence;
- hide poor outcomes;
- redefine scientific criteria without governance authority.

---

## 15. Data Intake Engine Architecture

The Data Intake Engine is the governed entry point for external data into durable MTS scientific use.

Its workflow is conceptually:

```text
External Source
      ↓
Acquisition
      ↓
Source Characterization
      ↓
Normalization
      ↓
Measurement Generation
      ↓
QA
      ↓
Validation
      ↓
Publication
      ↓
Research Nexus
```

The engine must preserve source provenance and must distinguish:

- received data;
- normalized data;
- deterministic measurements;
- validation results.

It must not silently repair missing or invalid data in a way that changes scientific meaning without recording the transformation.

---

## 16. Discovery Engine Architecture

The Discovery Engine converts governed inputs into reproducible evidence and findings.

Its purpose is not to confirm predefined narratives.

It must support both:

- hypothesis-driven analysis;
- discovery-oriented analysis.

It should be able to evaluate:

- relationships;
- temporal effects;
- context dependence;
- interactions;
- event families;
- contradictory behavior;
- instability;
- absence of meaningful effect.

Outputs must include enough provenance to reproduce the analysis.

---

## 17. Research Director Architecture

The Research Director is the scientific coordination intelligence of MTS.

It determines what research it proposes should happen next.

It does not schedule workers directly and does not control the independent
Research Admission or Knowledge Promotion gates.

Conceptually:

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
Required Engines
        ↓
Research Nexus
        ↓
Returned Evidence / Findings
        ↓
Research Director
        ↓
Follow-up / Convergence
        ↓
Knowledge Candidate
        ↓
Accountability — Knowledge Promotion
```

The Research Director must support iterative questioning.

It must be able to conclude:

- sufficient evidence;
- insufficient evidence;
- contradiction;
- no measurable relationship;
- missing data;
- missing tool/capability;
- research should continue;
- research should terminate.

Forced convergence is prohibited.

---

## 18. Accountability Engine Architecture

The Accountability Engine is the independent research gatekeeper of MTS.

It applies Charter-derived criteria expressed through current governance. Its
purpose is to prevent research resources and knowledge authority from being
granted solely by the component proposing the work or conclusion.

It controls two gates:

```text
GATE 1 — RESEARCH ADMISSION
Proposed Research Plan
        ↓
Accountability evaluation
        ↓
ADMIT / ADMIT_WITH_LIMITS / REVISION_REQUIRED / DUPLICATIVE / DEFER / REJECT

GATE 2 — KNOWLEDGE PROMOTION
Knowledge Candidate
        ↓
Accountability evaluation
        ↓
GATES_PASSED / GATES_PASSED_WITH_SCOPE / RESEARCH_REQUIRED /
INSUFFICIENT_EVIDENCE / BLOCKED
```

A gate verdict must identify:

- the proposal/candidate evaluated;
- policy and criteria version;
- evidence used by the gate;
- criteria passed;
- criteria failed;
- criteria inapplicable;
- blocking reason where applicable;
- scope/limits imposed;
- timestamp and producer identity.

The engine evaluates whether the required case has been demonstrated. It does
not substitute a new scientific hypothesis for the Research Director's
hypothesis.

Accountability must itself remain auditable, reproducible where deterministic
criteria apply, and challengeable through governed policy/lifecycle processes.

The same engine controls both research gates so Charter alignment is applied
consistently at admission and promotion, but the two verdict types remain
distinct governed artifacts.

Accountability does not approve individual investment Decisions. Decision
Engine retains the authority granted by Decision, Risk, and Automation policy.

---

## 19. Market Discovery Engine Architecture

The Market Discovery Engine is a live/current-state discovery component.

It should be architected for continuous or scheduled operation from the start, even if the first implementation runs manually.

It may:

- scan many instruments;
- evaluate known patterns;
- detect deviations from expected behavior;
- surface novel pattern candidates;
- connect live conditions to existing SoK;
- create Decision Requests;
- create Research Needs.

It should not require the Decision Engine to ingest raw exchange-scale data directly.

Low-latency internal paths are permitted provided material durable outputs are eventually published with governed identity and provenance.

---

## 20. Decision Engine Architecture

The Decision Engine converts current state plus governed knowledge into action.

Its inputs may include:

- current market state;
- applicable knowledge;
- uncertainty;
- risk constraints;
- portfolio constraints;
- policy;
- instrument characteristics;
- scalability;
- expected reward/risk;
- execution context.

Its outputs may include:

- no action;
- entry decision;
- direction;
- instrument choice;
- size;
- risk controls;
- management plan;
- exit conditions;
- Research Need.

The Decision Engine must preserve enough reasoning references and provenance to explain material decisions after the fact.

---

## 21. Learning & Governance Architecture

Learning & Governance closes the outcome loop.

It examines:

- what knowledge was used;
- what decision was made;
- what outcome occurred;
- whether the knowledge generalized;
- whether the decision process behaved as expected;
- whether evidence remains current;
- whether contradiction or decay has emerged.

It provides separation between:

- creating knowledge;
- using knowledge;
- evaluating whether that knowledge remains useful.

Promotion, degradation, supersession, and retirement criteria must be governed and objective.

---

## 22. Concurrency Model

Concurrency is architectural, even when initial execution is serial.

The Task Manager must be able to manage multiple tasks across independent workers.

A worker should not assume it is the only active process.

Engines must therefore avoid:

- global mutable filesystem state;
- unscoped temporary filenames;
- implicit singleton state;
- non-atomic shared writes;
- engine-private permanent registries.

Concurrency-sensitive implementation mechanisms belong in technical design.

---

## 23. Resource Model

Tasks may declare resource needs.

Examples:

- CPU;
- memory;
- GPU;
- local disk;
- network bandwidth;
- provider API quota;
- latency requirement;
- exclusive access requirement.

The Task Manager uses this metadata for scheduling.

Scientific components should not directly decide CPU-core allocation.

---

## 24. Retry and Idempotency

Where practical, engine tasks should be designed so retries do not corrupt durable state or duplicate canonical artifacts.

Task contracts should specify:

- whether a task is idempotent;
- how duplicate execution is detected;
- whether prior durable results may be reused;
- what constitutes a safe retry;
- what failures are terminal.

Canonical artifact identity should help prevent duplicate durable publication.

---

## 25. Failure Isolation

An engine failure must not corrupt the Research Nexus or unrelated engine state.

A failed task should produce explicit status.

Possible **task-execution** outcomes include:

```text
SUCCEEDED
FAILED_RETRYABLE
FAILED_TERMINAL
INSUFFICIENT_DATA
INSUFFICIENT_EVIDENCE
MISSING_CAPABILITY
CANCELLED
TIMED_OUT
BLOCKED_DEPENDENCY
```

Task-execution outcome is distinct from the semantic result produced by
an engine. For example, a Decision task may `SUCCEED` while its governed
Decision result is `NO_ACTION` or `RESEARCH_REQUIRED`.

Exact states belong in governance.

Partial outputs may be retained as diagnostic artifacts when useful but may not be mistaken for completed governed results.

---

## 26. Crash Recovery

The architecture must support recovery after:

- worker termination;
- Task Manager restart;
- computer restart;
- network interruption;
- temporary storage outage;
- provider failure.

Durable task state required for recovery must survive process loss.

The mature server system must not depend on a terminal session remaining open.

The first local implementation should follow the same durable task semantics.

---

## 27. Work Prioritization

The Task Manager must support governed priority.

Potential dimensions include:

- live-decision urgency;
- research dependency;
- scheduled intake;
- freshness requirement;
- campaign priority;
- resource cost;
- deadline;
- human override.

Priority is an operational scheduling concept.

Priority does not alter scientific validity.

---

## 28. Capability Expansion

A new engine may be added without restructuring existing engines when it provides:

1. a clear responsibility;
2. unique or useful capabilities;
3. governed task contracts;
4. governed output contracts;
5. required schemas;
6. authority boundaries;
7. lifecycle/retention behavior;
8. Task Manager registration;
9. tests proving conformance.

Illustrative future engines may include:

- Options Intelligence;
- Institutional Activity;
- Fundamental Intelligence;
- Portfolio/Risk;
- Execution;
- News/Event Intelligence;
- specialized model engines.

The list is not exhaustive.

---

## 29. Shared Core Services

Capabilities used by many engines may belong in `Core/` rather than being duplicated.

Examples:

- configuration;
- Task Manager services;
- Research Nexus client libraries;
- messaging;
- observability;
- identity utilities;
- schema validation;
- common time/calendar services.

Shared services must remain scientifically neutral unless explicitly granted domain authority.

---

## 30. Observability

Every engine must expose enough operational information to determine:

- worker availability;
- task currently executing;
- task duration;
- resource consumption;
- success/failure;
- retry count;
- output artifact references;
- implementation version;
- relevant errors.

Operational telemetry may be transient.

Material execution provenance must be durable when required to explain or reproduce results.

---

## 31. Testing Model

Engine validation must include:

### Unit Tests

Validate internal behavior in isolation.

### Contract Tests

Validate governed inputs/outputs and compatibility.

### Integration Tests

Validate interaction with the Task Manager and Research Nexus.

### End-to-End Tests

Validate real multi-engine workflows.

### Concurrency Tests

Validate safe behavior under simultaneous execution where relevant.

### Failure/Recovery Tests

Validate retry, interruption, restart, and partial-failure behavior.

The first v2 proof of concept should include at least one end-to-end path across Data Intake, Discovery, Research Director, Task Manager, and Research Nexus.

---

## 32. Initial v2 Engine Implementation

Initial v2 should implement only the minimum capabilities needed to prove the architecture while preserving mature boundaries.

Recommended first vertical slice:

```text
mts
 ↓
Task Manager
 ↓
Data Intake
 ↓
Research Nexus
 ↓
Discovery
 ↓
Research Nexus
 ↓
Research Director
 ↓
Research Nexus
```

Initial constraints may include:

```text
effective_concurrency = runtime_determined
single local machine
one ticker
one research campaign
```

These are implementation limits.

They are not architectural limits.

The same task, capability, artifact, and authority contracts must support later:

```text
many workers
many tickers
many simultaneous campaigns
live-market workloads
server deployment
```

---

## 33. Component Identity

Canonical engine identity is defined by enduring responsibility and declared capability.

Current engine responsibilities are:

```text
Data Intake Engine
Discovery Engine
Research Director
Accountability Engine
Market Discovery Engine
Decision Engine
Learning & Governance
```

Engine identity, routing, authority, dependency, and workflow must not derive from numbering, filename, directory location, repository hierarchy, or physical execution order.

---

## 34. Conformance Requirements

An engine conforms to this architecture when it:

1. has a defined responsibility;
2. declares governed capabilities;
3. consumes governed task/input contracts;
4. produces governed output contracts;
5. preserves required provenance;
6. does not own enterprise durable state;
7. does not depend on another engine's private filesystem;
8. uses the Task Manager for scheduled/routed work;
9. publishes durable state through the Research Nexus;
10. respects authority boundaries;
11. fails explicitly and safely;
12. supports retry/recovery appropriate to task type;
13. can operate under concurrency without relying on singleton assumptions;
14. remains replaceable behind stable contracts;
15. does not embed physical Research Nexus paths;
16. supports the mature server-scale model without requiring architectural replacement.

---

## 35. Companion Governance

This architecture should be supported by canonical unversioned companion documents including:

```text
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md

Governance/Contracts/TASK_CONTRACT.md
Governance/Contracts/ENGINE_CAPABILITY_CONTRACT.md
Governance/Contracts/ENGINE_RESULT_CONTRACT.md

Governance/Schemas/
Governance/Policies/
```

The exact set may evolve as implementation requirements become concrete.

---

## 36. Closing Principle

MTS should be able to replace, scale, duplicate, or distribute an engine without changing what the rest of the system believes that engine is.

> **Responsibility is architectural. Implementation is replaceable. Capability is declared. Work is governed. Durable state belongs to the Research Nexus.**
