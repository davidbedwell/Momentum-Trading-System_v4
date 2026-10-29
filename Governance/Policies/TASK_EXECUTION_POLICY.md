# Momentum Trading System — Task Execution Policy

**Status:** Canonical
**Authority:** Policy subordinate to `CHARTER.md`, canonical Architecture, and Governance Standards
**Applies To:** Governed task creation, admission verification, scheduling, execution, supervision, retry, recovery, completion, and failure handling

---

## 1. Purpose

This policy governs how authorized MTS work becomes executable work and how that
work is supervised through a terminal outcome.

It exists to ensure that execution is:

- authorized;
- dependency-aware;
- resource-bounded;
- observable;
- restartable where appropriate;
- idempotent where required;
- failure-explicit;
- auditable;
- independent of repository layout or component numbering.

Task execution is infrastructure coordination. It does not create scientific
authority, knowledge authority, or investment authority.

---

## 2. Governing Principle

> **Authority determines whether work may occur. Task Management determines when
> and where authorized work executes. The assigned component determines how to
> perform work within its contract.**

Task Manager must not infer authority from the existence of a task request.

---

## 3. Authority Boundaries

### 3.1 Research Work

Where Research Admission is required, Accountability controls the admission
gate.

Task Manager must verify a valid applicable Research Admission verdict before
releasing the governed research task.

Task Manager does not independently decide whether the research is scientifically
worth doing.

### 3.2 Decision and Trade Work

Task execution does not grant investment authority.

Decision Engine may exercise only the Decision authority granted by applicable
Decision, Risk, and Automation governance.

A task representing trade execution must carry the required Decision and
execution authority. The Task Manager must not create, reinterpret, improve, or
override that Decision.

Accountability Research Admission and Knowledge Promotion verdicts are not
individual-trade approvals.

### 3.3 Component Work

An assigned component may execute only capabilities granted to its governed
identity.

Physical directory location, process name, worker name, filename, or repository
position does not grant capability or authority.

---

## 4. Governed Task Requirement

Executable governed work must be represented by a Task artifact or equivalent
governed task state.

At minimum, executable task state must identify:

- task identity;
- task type;
- requested capability;
- producer/requester identity;
- applicable authority reference;
- input artifact references;
- dependency references;
- priority class;
- resource requirements or limits;
- retry policy;
- timeout/lease policy where applicable;
- idempotency/replay semantics;
- current task state;
- creation timestamp;
- lineage/correlation identifiers.

Task schemas may require additional fields by task class.

---

## 5. Task Lifecycle

The canonical task lifecycle must distinguish at least:

```text
PROPOSED
BLOCKED
READY
LEASED
RUNNING
SUCCEEDED
FAILED_RETRYABLE
FAILED_TERMINAL
CANCELLED
```

Additional governed states may be defined by schema or contract.

A task may not enter `READY` until required authority and dependencies are
satisfied.

A task may not enter `RUNNING` merely because a worker is available.

---

## 6. Readiness Evaluation

Before a task becomes `READY`, Task Manager must verify all applicable
requirements, including:

1. valid task schema;
2. recognized task type;
3. authorized requester;
4. required admission/authority state;
5. required dependencies satisfied;
6. required inputs available and valid;
7. required component capability available;
8. applicable resource ceiling permits release;
9. no active cancellation or policy block;
10. required execution configuration is valid.

Failure of readiness evaluation must produce an explicit blocked or terminal
state rather than silent non-execution.

---

## 7. Dependency Handling

Dependencies must be represented explicitly.

Task Manager must not infer dependencies from:

- directory order;
- filenames;
- component numbering;
- source-code import order;
- historical execution habits.

A dependent task may be released only when its required dependency conditions
are satisfied.

Dependency failure must propagate according to declared dependency semantics,
not by assumption.

Circular dependencies must be detected and rejected or blocked explicitly.

---

## 8. Scheduling

Task Manager owns scheduling of governed executable work.

Scheduling may consider:

- priority;
- dependency readiness;
- resource availability;
- capability availability;
- deadline/latency requirement;
- fairness;
- starvation prevention;
- task age;
- retry state;
- operational policy.

Scheduling must not alter the scientific conclusion, Decision content, or
authority represented by the task.

---

## 9. Priority

Priority must be explicit and governed.

Priority may account for categories such as:

- safety/risk protection;
- active position management;
- time-sensitive Decision support;
- required system recovery;
- dependency-unblocking work;
- admitted research;
- maintenance;
- background discovery.

Exact priority classes and weights belong in configuration/schema where
appropriate.

Priority does not override missing authority, failed dependencies, or hard
resource limits.

Starvation of valid lower-priority work must be detectable.

---

## 10. Resource Governance

Task Manager shall discover effective compute and resource capacity at runtime
and dynamically determine safe and efficient concurrency according to:

- task resource requirements;
- task priority;
- dependency state;
- capability requirements;
- CPU availability;
- memory availability;
- storage and I/O pressure;
- network/API capacity;
- provider quotas;
- latency-sensitive reserved capacity;
- applicable policy and configuration.

Resource ceilings must be configurable and observable.

Policy must not hard-code a specific current machine, CPU count, worker count,
or daily throughput limit as permanent architecture.

Configured worker counts, where used, are optional ceilings, reservations, or
deployment overrides. They are not fixed allocations and do not define how many
execution instances an engine owns.

Governed configuration may additionally define limits for:

- concurrent tasks;
- tasks per capability/component;
- CPU;
- memory;
- storage I/O;
- network/API usage;
- provider quotas;
- market-data subscriptions;
- daily/periodic intake volume;
- research budget;
- latency-sensitive reserved capacity.

Task Manager must enforce the currently effective limits while using available
resources efficiently.

Increasing available hardware may increase safe execution capacity, but it does
not automatically increase scientific, knowledge, investment, or automation
authority.

---

## 11. Concurrency

Engines define capabilities. Tasks define work. Workers are execution instances
dynamically allocated as needed.

Workers are not permanently assigned to engines and do not inherently
correspond to CPU cores.

Task Manager dynamically allocates eligible execution instances according to
current work and discovered resource capacity.

Concurrency is permitted only when tasks can safely and efficiently execute in
parallel under their contracts and resource limits.

Concurrency control must prevent:

- conflicting writes;
- duplicate non-idempotent effects;
- unsafe shared-state mutation;
- resource exhaustion;
- violation of provider limits;
- simultaneous ownership of an exclusive task.

A CPU core is a compute resource, not a worker identity. Depending on workload
characteristics, safe and efficient concurrency may be lower than, equal to, or
greater than physical core count.

---

## 12. Leasing and Ownership

Where distributed or interruptible execution is possible, Task Manager should
use governed leases or equivalent ownership state.

A lease must identify:

- task;
- worker;
- acquisition time;
- expiration/renewal condition;
- execution attempt.

A worker must not indefinitely own a task merely because it once started it.

Expired ownership must become recoverable according to task semantics.

---

## 13. Heartbeats and Liveness

Long-running tasks should emit sufficient liveness state to distinguish:

- actively progressing work;
- stalled work;
- disconnected worker;
- expired lease;
- completed work whose acknowledgement was lost.

Heartbeat frequency belongs in configuration or task-class contracts.

Absence of a heartbeat is operational evidence, not automatically scientific
evidence that the task's hypothesis failed.

---

## 14. Timeouts

Timeouts must be task-class appropriate and configurable.

A timeout must result in an explicit execution state.

Timeout does not itself mean:

- the research question is false;
- the Knowledge Candidate is invalid;
- the Decision thesis is invalid;
- the underlying data does not exist.

It means the execution attempt failed to complete within its governed limit.

---

## 15. Retry Policy

Retries must be bounded and reason-aware.

A retry may be appropriate for transient failures such as:

- temporary provider unavailability;
- worker interruption;
- recoverable network failure;
- expired lease;
- transient resource shortage.

Automatic retry must not be used to conceal deterministic defects, invalid
inputs, failed authority checks, or policy violations.

Retry policy must define, where applicable:

- maximum attempts;
- delay/backoff;
- retryable failure classes;
- terminal failure classes;
- whether a new worker may acquire the task;
- idempotency requirements.

---

## 16. Idempotency and Duplicate Execution

Task classes capable of producing persistent side effects must define
idempotency or duplicate-prevention behavior.

Retries and recovery must not silently create duplicate:

- canonical artifacts;
- research publications;
- lifecycle transitions;
- orders;
- trades;
- external notifications;
- destructive operations.

Where an operation cannot be made idempotent, execution must use stronger
ownership and reconciliation controls.

---

## 17. Checkpoint and Restart

Long-running or expensive work should support checkpoint/restart when technically
and scientifically valid.

A checkpoint must not be treated as a completed scientific result.

Restart behavior must preserve:

- task identity;
- attempt lineage;
- input identity/version;
- relevant configuration;
- deterministic/reproducibility state where required.

If safe restart cannot be demonstrated, the task must restart from a valid
boundary or fail explicitly.

---

## 18. Failure Classification

Execution failures must be classified.

At minimum, MTS must distinguish:

```text
AUTHORITY_FAILURE
DEPENDENCY_FAILURE
INPUT_FAILURE
CAPABILITY_FAILURE
RESOURCE_FAILURE
TRANSIENT_EXECUTION_FAILURE
TIMEOUT_FAILURE
VALIDATION_FAILURE
DETERMINISTIC_EXECUTION_FAILURE
CANCELLED
UNKNOWN_FAILURE
```

Failure taxonomy may be extended by governed schema.

Scientific insufficiency such as `INSUFFICIENT_EVIDENCE` is not interchangeable
with infrastructure execution failure.

---

## 19. Terminal Failure

A task becomes terminal when:

- policy forbids retry;
- retry budget is exhausted;
- required authority is invalid or revoked;
- required input cannot be made valid;
- required capability is unavailable with no governed recovery path;
- deterministic failure persists;
- cancellation is final;
- another policy-defined terminal condition applies.

Terminal failure must preserve enough evidence for diagnosis and governed
follow-up.

---

## 20. Cancellation

Cancellation authority must be explicit.

Cancellation may be initiated by authorized:

- human control;
- governing workflow;
- requester where permitted;
- risk/safety mechanism;
- superseding task/workflow;
- policy enforcement.

Cancellation must not silently erase execution history.

For side-effecting work, cancellation must distinguish between:

- not started;
- safely stopped before effect;
- partially executed;
- externally committed;
- reconciliation required.

---

## 21. Completion

A task may enter `SUCCEEDED` only when its execution contract's completion
conditions are satisfied.

Process exit code alone is insufficient when the contract requires:

- output validation;
- artifact publication;
- provenance;
- schema validation;
- downstream acknowledgement;
- external-effect reconciliation.

Task success means the task contract completed. It does not by itself mean the
scientific conclusion is true or economically useful.

---

## 22. Output Publication

Task outputs must be published through the governed interface appropriate to the
artifact type.

Workers must not bypass artifact governance by writing authoritative results to
private or incidental locations.

Publication must preserve provenance sufficient to identify:

```text
task
→ attempt
→ worker/component
→ inputs
→ configuration
→ outputs
→ validation state
```

---

## 23. Observability

Task execution must expose machine-readable operational state sufficient to
answer:

- what is queued;
- what is blocked and why;
- what is ready;
- what is running;
- who/what owns it;
- how long it has run;
- what resources it is consuming where measurable;
- what failed;
- whether it will retry;
- what completed;
- what downstream work became eligible.

Human interfaces may visualize this state but must not become the source of
task truth.

---

## 24. Audit

Material execution transitions must be auditable.

Audit history must preserve enough information to reconstruct:

```text
request
→ authority/admission verification
→ readiness
→ scheduling
→ lease/worker assignment
→ attempts/retries
→ output publication
→ completion/failure/cancellation
```

Audit retention follows applicable artifact and storage-retention governance.

---

## 25. Recovery After Process or System Restart

Persistent task state must support recovery after Task Manager or system
restart.

On recovery, Task Manager must reconcile tasks that were:

- queued;
- blocked;
- leased;
- running;
- retrying;
- awaiting acknowledgement.

It must not assume that every previously running task failed before checking
lease, output, and side-effect state.

For external side effects, reconciliation must precede blind replay.

---

## 26. Provider and External-System Limits

Tasks interacting with external providers must obey applicable:

- rate limits;
- concurrency limits;
- quotas;
- market-session constraints;
- authentication/authorization limits;
- contractual restrictions.

Provider throttling should normally be treated as an operational/resource state,
not a scientific finding.

---

## 27. Market-Time Sensitivity

Time-sensitive market work may receive governed priority and reserved resources.

Task metadata should distinguish where lateness changes the usefulness or safety
of the result.

A stale time-sensitive task must not be executed merely because it eventually
reached the front of a queue if its contract says the result is no longer
actionable.

---

## 28. Research Execution

For research governed by Research Admission:

```text
Proposed Research Plan
        ↓
Accountability — Research Admission
        ↓
Task Request(s)
        ↓
Task Manager readiness/dependency evaluation
        ↓
Scheduling / execution
        ↓
Evidence / Findings
        ↓
Research Director
```

Task Manager may reject or block execution for operational reasons even when
Research Admission passed.

Operational blocking does not revoke the scientific admission verdict.

---

## 29. Decision and Trade Execution

For investment actions:

```text
Governed Decision
        ↓
required Risk / Automation / execution authority
        ↓
authorized execution task
        ↓
Task Manager / execution capability
        ↓
broker or execution venue
        ↓
reconciliation / resulting state
```

Task Manager must not change:

- instrument;
- direction;
- size;
- entry logic;
- risk limits;
- exit logic;

unless an applicable execution contract explicitly grants a bounded execution
choice.

Any such bounded choice must remain subordinate to the governing Decision and
risk authority.

---

## 30. Human Intervention

Authorized human operators may inspect task state and perform only controls
granted by policy, such as:

- pause;
- resume;
- cancel;
- retry;
- reprioritize within allowed bounds;
- resolve an operational block;
- place the system into a safer operating mode.

Human intervention must be recorded.

A graphical control interface does not create new authority merely by exposing
a button.

---

## 31. Configuration

Operational values that may change with hardware, providers, workload, or
deployment belong in governed configuration rather than this policy whenever
possible.

Examples include:

- worker counts;
- concurrency ceilings;
- timeout durations;
- retry counts;
- backoff intervals;
- heartbeat intervals;
- lease durations;
- daily intake caps;
- provider quotas;
- reserved capacity.

Configuration must identify version/effective state sufficient for audit.

---

## 32. Prohibited Behavior

MTS must not:

- execute gated research without required Research Admission;
- treat task creation as authorization;
- route by repository position or component number;
- silently ignore blocked tasks;
- retry indefinitely;
- silently duplicate side effects;
- equate execution failure with scientific falsification;
- equate execution success with scientific validity;
- allow Task Manager to rewrite research or Decision intent;
- let a worker expand its own authority;
- hard-code temporary hardware constraints as permanent policy;
- discard material failure/retry lineage needed for audit or recovery.

---

## 33. Minimum Initial Implementation

Initial Task Manager implementation should prove:

1. governed Task artifact validation;
2. authority/admission verification;
3. dependency blocking and release;
4. configurable priority;
5. configurable concurrency/resource ceilings;
6. worker lease/ownership;
7. bounded retry;
8. timeout handling;
9. explicit terminal failure;
10. idempotent or reconciled output publication;
11. restart recovery;
12. machine-readable queue/running/blocked/completed state;
13. audit lineage;
14. refusal to execute admitted-research classes without Research Admission;
15. preservation of Decision authority boundaries.

---

## 34. Closing Principle

> **Task execution is the governed conversion of authorized intent into bounded,
> observable work. It may coordinate execution, but it may not manufacture the
> authority, science, knowledge, or investment Decision that the work serves.**
