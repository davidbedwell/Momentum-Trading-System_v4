# Momentum Trading System — Task Management Standard

**Status:** Canonical
**Authority:** Governing standard subordinate to `CHARTER.md`, the canonical MTS v2 architecture set, `IDENTITY_STANDARD.md`, `ARTIFACT_GOVERNANCE_STANDARD.md`, `SCHEMA_STANDARD.md`, `STORAGE_RETENTION_STANDARD.md`, and `ENGINE_INTERFACE_STANDARD.md`.

---

## 1. Purpose

This standard defines how MTS creates, prioritizes, schedules, routes, executes, retries, blocks, resumes, cancels, times out, records, and recovers governed work.

It governs the Task Manager and all components that submit or execute MTS tasks.

This standard applies to:

- Data Intake work;
- Discovery work;
- Research Director work;
- Market Discovery work;
- Decision work;
- Learning & Governance work;
- migration jobs;
- validation jobs;
- maintenance jobs;
- future engine work.

---

## 2. Governing Principle

> **Work is governed state. Execution is a temporary attempt to complete that work.**

A task must remain understandable independently of:

- which worker first attempted it;
- which process was running;
- where the queue lived;
- whether the machine restarted;
- whether the first attempt failed.

---

## 3. Design With the End in Mind

Task management must be designed for the mature MTS deployment from the beginning.

The same task model must support evolution from:

```text
single Mac
one active worker
sequential execution
```

to:

```text
server deployment
multiple workers
parallel execution
resource-aware scheduling
live and batch workloads
long-running research campaigns
```

Initial worker count may be one.

The task model must not assume one.

---

## 4. Task Manager Role

The Task Manager is a permanent first-class MTS component.

It owns system-wide coordination of governed work, including:

- task acceptance;
- identity;
- dependency tracking;
- priority;
- capability routing;
- worker assignment;
- retries;
- timeouts;
- cancellation;
- recovery;
- state transitions;
- concurrency limits;
- resource-aware scheduling;
- downstream release.

The Task Manager does not perform scientific interpretation or make investment decisions.

---

## 5. Submission Sources

Governed tasks may be submitted by:

- `mts` control interface;
- Research Director;
- Market Discovery;
- Decision;
- Learning & Governance;
- authorized automation;
- authorized human operator;
- future services.

All submissions enter the same governed task system.

A component must not create a private parallel scheduler for work that belongs to MTS task management.

---

## 6. Task Identity

Every governed task has a stable `task_id`.

The task represents the requested work.

Retries do not create a new task unless the work request itself materially changes.

Execution attempts receive separate `execution_id` values.

---

## 7. Task Request

A governed Task Request should include at least:

```text
task_id
task_type
requested_capability
requester
created_at
priority
input_refs
dependencies
policy_refs where applicable
schema_id
schema_version
state
```

Additional fields may include:

```text
deadline
freshness_requirement
resource_requirements
retry_policy
timeout
campaign_id
research_plan_id
decision_id
instrument_ref
```

Exact structure belongs in Governance/Schemas.

---

## 8. Task Type

`task_type` identifies the semantic unit of work.

Examples may include:

```text
DATA_INGEST
DATA_VALIDATE
FEATURE_COMPUTE
DISCOVERY_SCAN
RESEARCH_ANALYSIS
RESEARCH_PLAN_EXECUTION
MARKET_SCAN
DECISION_EVALUATION
OUTCOME_EVALUATION
CACHE_RETIREMENT
MIGRATION
```

Task types must be governed and extensible.

---

## 9. Requested Capability

Routing should depend on required capability rather than hard-coded engine numbers.

Examples:

```text
capability:data-intake
capability:relationship-discovery
capability:research-direction
capability:market-discovery
capability:decision
capability:learning-governance
```

One engine may expose multiple compatible capabilities.

---

## 10. Task State vs Execution State

Task state and execution-attempt state are distinct.

A task may persist across multiple execution attempts.

Illustrative task states:

```text
CREATED
READY
BLOCKED
QUEUED
RUNNING
SUCCEEDED
FAILED
CANCELLED
EXPIRED
```

Illustrative execution states:

```text
STARTED
SUCCEEDED
FAILED_RETRYABLE
FAILED_TERMINAL
CANCELLED
TIMED_OUT
LOST_WORKER
```

Exact vocabularies belong in schemas and policy.

---

## 11. Semantic Result vs Task State

A successfully executed task may produce a semantic result such as:

```text
INSUFFICIENT_EVIDENCE
MISSING_CAPABILITY
NO_ACTION
RESEARCH_REQUIRED
```

These are not task-execution failures.

The Task Manager records completion and output references.

The consuming domain interprets the semantic result.

---

## 12. Durable Task State

Task state required for:

- restart recovery;
- provenance;
- dependency tracking;
- downstream release;
- audit;

is Class II Research Nexus state.

Examples:

```text
Task Request
dependency record
material execution record
terminal task result
```

---

## 13. Transient Scheduling State

Reconstructable operational state may be Class III.

Examples:

- in-memory ready queue;
- worker-local dispatch cache;
- scheduling heap;
- temporary lock;
- heartbeat cache.

The Task Manager must be able to reconstruct required work state from durable records after restart.

---

## 14. Dependency Graph

Tasks may depend on other tasks or artifacts.

Dependencies must be explicit.

A task may become `READY` only when its required dependencies are satisfied.

Examples:

```text
Data Intake
   ↓
Validation
   ↓
Discovery
   ↓
Research Director
```

or:

```text
Research Plan
   ├── Discovery Task A
   ├── Data Intake Task B
   └── Analysis Task C
         ↓
   Research Director continuation
```

The architecture must support arbitrary acyclic task dependencies where practical.

---

## 15. Dependency Types

Dependency semantics may include:

```text
REQUIRES_SUCCESS
REQUIRES_COMPLETION
REQUIRES_ARTIFACT
REQUIRES_CAPABILITY
REQUIRES_HUMAN_INPUT
```

Exact controlled vocabulary belongs in Governance/Schemas.

---

## 16. Dependency Failure

If a required dependency fails terminally, downstream work must not silently run as though the dependency succeeded.

The dependent task should become:

- blocked;
- failed;
- rerouted;
- or revised;

according to policy.

---

## 17. Priority

Task priority must be explicit and policy-driven.

Potential priority dimensions include:

- live-market urgency;
- decision freshness;
- active research dependency;
- human-requested urgency;
- maintenance priority;
- resource cost;
- starvation prevention.

Priority must not be encoded only by insertion order.

---

## 18. Priority Classes

MTS may define classes such as:

```text
CRITICAL
HIGH
NORMAL
LOW
BACKGROUND
```

Exact semantics belong in policy.

Live Decision work may outrank long-running historical research when freshness requires it.

---

## 19. Starvation Prevention

Low-priority work must not remain blocked forever merely because higher-priority work continues to arrive.

The scheduler should support aging or another governed fairness mechanism where appropriate.

---

## 20. Deadlines

Tasks may declare deadlines.

Examples:

- decision must complete before market condition is stale;
- research response needed before dependent evaluation;
- maintenance task required before retention deadline.

Missed deadlines must be explicit.

---

## 21. Freshness

Freshness is distinct from timeout.

A task may complete technically but become scientifically useless because its market inputs are stale.

Freshness requirements should be part of the Task Request or domain policy where material.

---

## 22. Expiration

A task may expire when:

- deadline passes;
- market state becomes stale;
- requester cancels;
- dependent context is superseded;
- policy no longer permits execution.

Expired work should not be executed merely because it is still sitting in a queue.

---

## 23. Resource Requirements

Tasks may declare estimated resource needs.

Examples:

```text
CPU
memory
storage
network
provider quota
GPU
exclusive dataset access
```

Resource requirements help the Task Manager avoid overload.

---

## 24. Resource Limits

The Task Manager must respect configured resource limits.

Initial deployment may use:

```text
max_workers = 1
```

This is an operational limit, not an architectural assumption.

Future server deployment may raise limits without changing task contracts.

---

## 25. Worker Eligibility

A worker is eligible when:

- capability matches;
- interface/schema versions are compatible;
- required resources are available;
- policy allows assignment;
- worker is healthy.

The Task Manager must route by governed capability and task requirements, not by filename, directory location, repository hierarchy, component numbering, or physical execution order.

---

## 26. Assignment

A task assignment should create or reference an execution attempt.

Assignment metadata may include:

```text
task_id
execution_id
worker_id
assigned_at
lease/heartbeat policy
```

Assignment must be recoverable after interruption.

---

## 27. Lease / Heartbeat

Long-running tasks may use lease or heartbeat semantics.

If a worker stops reporting:

- the execution may be marked lost;
- the task may become retryable;
- partial outputs must not be treated as complete.

Heartbeat loss is an operational failure, not a scientific conclusion.

---

## 28. Retry Policy

Retry behavior must be explicit.

A retry policy may specify:

```text
max_attempts
backoff
retryable_failure_types
deadline interaction
resource changes
```

Unbounded retry is prohibited.

---

## 29. Retryable Failure

Examples may include:

- transient provider outage;
- temporary Nexus unavailability;
- worker crash;
- temporary resource exhaustion;
- network interruption.

Retryability is a policy/contract property.

---

## 30. Terminal Failure

Examples may include:

- unsupported schema;
- invalid task definition;
- impossible parameter;
- unauthorized operation;
- corrupted required source;
- irreconcilable dependency failure.

Terminal failures require operator or upstream logic to revise the work before another attempt.

---

## 31. Missing Capability

A task may execute successfully and determine that MTS lacks required capability.

The semantic result is:

```text
MISSING_CAPABILITY
```

The Task Manager should record task completion according to contract and allow creation of an appropriate Research Need or capability request.

It must not retry indefinitely when no eligible capability exists.

---

## 32. Insufficient Evidence

A research task may complete successfully with:

```text
INSUFFICIENT_EVIDENCE
```

The Task Manager treats this as a completed semantic result.

The Research Director decides what to do next.

---

## 33. Cancellation

Authorized actors may cancel work.

Cancellation must distinguish:

- task not yet started;
- active execution cancellation;
- downstream dependency cancellation.

A cancelled execution must not publish incomplete artifacts as complete.

---

## 34. Timeout

Timeout policy applies to execution duration.

Timeout should record:

```text
task_id
execution_id
timeout_limit
elapsed_time
diagnostics
```

A timeout may be retryable or terminal according to policy.

---

## 35. Checkpointing

Long-running tasks may support governed checkpoints.

Checkpointing may be useful when:

- computation is expensive;
- tasks may run for hours;
- restart cost is high.

Checkpoints are operational artifacts and must not be confused with published scientific outputs.

---

## 36. Resume

A resumed task must preserve:

- original `task_id`;
- prior execution history;
- checkpoint provenance;
- new `execution_id`.

Resume must not conceal prior interruption.

---

## 37. Idempotency

Task submission and execution should be idempotent where practical.

Duplicate submission of the same logical work must not create uncontrolled duplication.

Possible strategies include:

- caller-provided idempotency key;
- deterministic task key;
- existing active-task lookup;
- artifact-exists short-circuit.

Exact strategy may differ by task family.

---

## 38. Duplicate Task Detection

Duplicate detection must not collapse genuinely distinct work.

Two tasks may look similar but differ in:

- input versions;
- time range;
- research question;
- policy;
- freshness;
- instrument context.

Duplicate rules must be domain-aware.

---

## 39. Task Revision

If requested work changes materially, create a new task identity or explicitly version/revise the Task Request according to schema.

Do not mutate a running task's scientific meaning invisibly.

---

## 40. Task Provenance

Every task should preserve:

```text
requester
created_at
inputs
dependencies
policy/context
reason
campaign/research linkage where relevant
```

This allows MTS to answer:

> Why did this work run?

---

## 41. Execution Provenance

Every execution should preserve:

```text
execution_id
task_ref
worker_id
engine_id
software version
started_at
completed_at
execution_state
output_refs
diagnostics_refs
```

---

## 42. Output Publication

The Task Manager must not infer success solely from process exit code.

A task requiring governed outputs is not complete until required output publication succeeds.

---

## 43. Partial Success

Multi-output tasks may produce partial results.

Partial success must be explicit.

The contract must define whether:

- partial output is publishable;
- task remains failed;
- downstream tasks may consume successful subsets.

Silent partial success is prohibited.

---

## 44. Atomicity

Where a task's outputs form one logical publication, publication should be atomic or transactionally represented.

Downstream consumers must not see an artifact package as complete when required members are missing.

---

## 45. Downstream Release

When a task reaches the required completion state, the Task Manager reevaluates dependent tasks.

Dependency release should be deterministic and auditable.

---

## 46. Research Plan Expansion

A Research Plan may generate multiple Task Requests.

The Task Manager manages execution ordering and concurrency.

The Research Director remains responsible for scientific intent and deciding whether more research is needed after results return.

---

## 47. Iterative Research Loop

Conceptually:

```text
Research Director
      ↓
Research Plan
      ↓
Task Manager
      ↓
Engine tasks
      ↓
Artifacts / findings
      ↓
Research Director
      ↓
next question / convergence / insufficient evidence
```

The Task Manager coordinates work but does not decide the next scientific question.

---

## 48. Market Discovery Loop

Market Discovery may generate candidate events or Decision Requests.

Its high-frequency operational work may be prioritized separately from slow historical research.

Task policy should permit distinct workload classes without separate schedulers.

---

## 49. Decision Work

Decision tasks may have strict freshness/deadline requirements.

A stale Decision task should expire rather than produce an apparently current recommendation from obsolete inputs.

---

## 50. Maintenance Work

Maintenance tasks may include:

- cache retirement;
- integrity verification;
- backup verification;
- migration;
- retention evaluation;
- index maintenance.

Maintenance uses the same governed task framework.

---

## 51. Daily Intake Limit

Operational policy may impose temporary limits such as:

```text
one new unprocessed source item per day
```

on resource-constrained hardware.

Such limits belong in configuration/policy.

They must not be encoded as permanent architectural assumptions.

---

## 52. Parallelism

Future deployment may execute multiple independent tasks concurrently.

The scheduler must respect:

- resource limits;
- dependencies;
- exclusive resources;
- data/provider quotas;
- priority;
- freshness.

---

## 53. One Task Per Worker

A worker may initially execute one active task at a time.

Future workers may support internal concurrency only if explicitly governed and observable.

The Task Manager must retain system-wide authority over resource concurrency.

---

## 54. Exclusive Tasks

Some tasks may require exclusive access to:

- a migration target;
- a mutable index;
- a provider quota;
- a maintenance lock.

Exclusivity must be declared and scheduled, not implemented through hidden ad hoc locks alone.

---

## 55. Queue Persistence

The exact queue technology is implementation detail.

The durable Task Request and dependency state are authoritative.

A queue may be:

- in memory;
- database-backed;
- message-broker-backed;
- hybrid.

Changing queue technology must not change task semantics.

---

## 56. Crash Recovery

After Task Manager restart, the system must reconstruct:

- nonterminal tasks;
- dependencies;
- execution attempts;
- lost-worker states;
- retry eligibility;
- deadlines/expiration.

A restart must not silently lose governed work.

---

## 57. Orphaned Executions

If the Task Manager restarts while workers continue running, the system must reconcile execution state.

Possible mechanisms include:

- execution lease;
- worker heartbeat;
- execution lookup;
- eventual timeout.

Duplicate concurrent execution must be prevented or made idempotent where required.

---

## 58. Audit

Material task lifecycle transitions should be auditable.

Examples:

```text
CREATED
READY
ASSIGNED
STARTED
RETRIED
BLOCKED
SUCCEEDED
FAILED
CANCELLED
EXPIRED
```

Audit should be append-oriented.

---

## 59. Observability

Task Manager observability should include:

- queue depth;
- ready tasks;
- blocked tasks;
- running tasks;
- worker status;
- retries;
- failures;
- task age;
- deadline risk;
- resource use.

Operational observability must not require reading private worker files.

---

## 60. Human Control

The operator should be able to inspect:

- task status;
- reason for blocking;
- dependencies;
- current execution;
- failure diagnostics;
- retry history.

Human control interfaces should use governed Task Manager services rather than manipulating queue files directly.

---

## 61. Safety of Operator Actions

Administrative actions such as:

- retry;
- cancel;
- reprioritize;
- release a manual block;

must be explicit and auditable.

Destructive bulk task deletion should require strong safeguards.

---

## 62. Task Retention

Active tasks and material execution records are Class II.

Completed task history may later become Semi-Permanent or archived according to retention policy.

Task history required for:

- scientific provenance;
- decisions;
- reproducibility;
- audit;

must remain resolvable.

---

## 63. Logs vs Task Records

Logs supplement task records.

They do not replace them.

A task's canonical:

- identity;
- state;
- dependencies;
- outputs;
- execution history;

must be machine-readable structured state.

---

## 64. Schema Compatibility

The Task Manager must validate Task Request schema/interface compatibility before assignment.

Unsupported incompatible task versions must fail explicitly.

---

## 65. Authorization

Not every component may submit every task type.

Task submission authority should be governed.

Examples:

- Research Director may request research work;
- Decision may request research needs within defined scope;
- ordinary engines may not submit unrestricted administrative deletion tasks.

---

## 66. Security

Task payloads must not carry secrets unnecessarily.

Secrets should be resolved through governed configuration/credential services.

Task logs must not leak credentials.

---

## 67. Initial v2 Implementation

The first Task Manager implementation should support:

1. durable Task Request storage;
2. durable dependency records;
3. one local worker at a time;
4. capability-based routing;
5. task/execution identity separation;
6. explicit task and execution states;
7. retryable vs terminal failure;
8. restart recovery;
9. output references;
10. downstream dependency release;
11. operator status inspection.

It need not begin with a distributed message broker.

The contracts must permit one later.

---

## 68. Initial Proof

A minimal v2 proof should demonstrate:

```text
mts submit
    ↓
Task Request
    ↓
Task Manager
    ↓
eligible worker
    ↓
Execution Record
    ↓
Research Nexus output
    ↓
Task SUCCEEDED
    ↓
dependent task becomes READY
```

Then restart the Task Manager and prove unfinished durable work is preserved.

---

## 69. Testing Requirements

Task management tests must include:

- task identity uniqueness;
- execution identity separation;
- dependency blocking/release;
- capability routing;
- priority ordering;
- retry policy;
- terminal failure;
- cancellation;
- timeout;
- expiration;
- restart recovery;
- lost worker handling;
- duplicate submission/idempotency;
- output publication failure;
- one-worker resource limit;
- future multi-worker simulation.

---

## 70. Prohibited Practices

The following are prohibited:

- private per-engine schedulers for governed work;
- relying solely on in-memory task state;
- hard-coded component-number routing;
- infinite retries;
- silent dependency bypass;
- treating timeout as insufficient evidence;
- treating `NO_ACTION` as task failure;
- queue position as durable identity;
- direct manipulation of private queue files by downstream engines;
- silent loss of tasks after restart.

---

## 71. Conformance

A task system conforms when it:

1. preserves durable Task Requests;
2. separates task and execution identity;
3. tracks explicit dependencies;
4. routes by governed capability;
5. uses policy-driven priority;
6. distinguishes retryable and terminal failure;
7. distinguishes execution state from semantic result;
8. supports restart recovery;
9. preserves execution history;
10. respects resource/concurrency limits;
11. supports cancellation/timeout/expiration;
12. releases downstream work deterministically;
13. remains implementation-neutral regarding queue technology;
14. supports future server-scale concurrency without redesign.

---

## 72. Companion Governance

This standard operates with:

```text
Governance/Standards/IDENTITY_STANDARD.md
Governance/Standards/ARTIFACT_GOVERNANCE_STANDARD.md
Governance/Standards/SCHEMA_STANDARD.md
Governance/Standards/STORAGE_RETENTION_STANDARD.md
Governance/Standards/ENGINE_INTERFACE_STANDARD.md
Governance/Standards/CONFIGURATION_STANDARD.md
Governance/Standards/TEST_AND_VALIDATION_STANDARD.md

Governance/Contracts/TASK_REQUEST_CONTRACT.md
Governance/Contracts/EXECUTION_CONTRACT.md
Governance/Schemas/
```

---

## 73. Closing Principle

MTS must always be able to answer:

> **What work was requested, why was it requested, what must happen first, who is eligible to execute it, what happened on each attempt, and what should happen next if the machine restarts?**

If those answers live only in a running process or a private engine queue, task management is not sufficiently governed.
