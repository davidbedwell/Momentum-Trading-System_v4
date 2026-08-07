# Momentum Trading System — Observability and Audit Standard

**Status:** Canonical

## 1. Purpose

This standard defines how Momentum Trading System (MTS) exposes, records, correlates, retains, and audits operational and scientific activity.

It governs:

- runtime status;
- structured logs;
- metrics;
- traces/correlation;
- task observability;
- engine observability;
- Research Nexus observability;
- audit records;
- health reporting;
- alerts;
- retention of operational vs material records;
- operator visibility;
- restart/recovery diagnostics.

Its purpose is to ensure MTS can explain both **what is happening now** and **what materially happened in the past** without treating logs as the canonical system of record.

## 2. Governing Principle

> **Operational telemetry explains system behavior; durable audit records explain material history. Neither substitutes for canonical domain state.**

## 3. Observability vs Audit

MTS distinguishes:

```text
OBSERVABILITY
```

from:

```text
AUDIT
```

Observability is primarily concerned with:

- current behavior;
- runtime health;
- performance;
- failures;
- resource use;
- queue/work status.

Audit is primarily concerned with:

- material state transitions;
- authoritative actions;
- provenance;
- approvals;
- lifecycle changes;
- decisions;
- governance-relevant history.

They may share identifiers and infrastructure, but their retention and authority differ.

## 4. Logs Are Not Canonical State

MTS must never require parsing free-form logs to determine canonical:

- Task state;
- artifact identity;
- Research Plan state;
- Decision state;
- Outcome state;
- lifecycle state;
- approval state;
- retention class.

These must remain structured governed records.

## 5. Structured Logging

Material runtime components should emit structured logs.

Structured records should include, when applicable:

```text
timestamp
severity
component
engine_id
worker_id
task_id
execution_id
artifact_ref
campaign_id
research_plan_id
decision_id
event_type
message
```

Additional context may be included when useful.

## 6. Correlation

Cross-component work must be traceable through stable correlation identifiers.

At minimum, task/execution flows should support:

```text
task_id
execution_id
```

Research flows may additionally use:

```text
campaign_id
research_plan_id
question_id
```

Decision flows may additionally use:

```text
decision_id
outcome_id
evaluation_id
```

## 7. Traceability Across Components

MTS should be able to follow a material workflow conceptually as:

```text
Task Request
→ worker assignment
→ execution
→ artifact publication
→ downstream task release
→ Decision / Outcome / Learning
```

without scraping private files or console output.

## 8. Task Manager Observability

The Task Manager must expose enough structured status to determine:

- queued tasks;
- ready tasks;
- blocked tasks;
- running tasks;
- completed tasks;
- failed tasks;
- retry count;
- age;
- priority;
- dependency status;
- active worker;
- deadline/freshness risk.

## 9. Engine Observability

Every engine must expose enough operational information to determine:

- worker availability;
- current task;
- execution duration;
- resource consumption;
- success/failure;
- retry status;
- output references;
- implementation version;
- relevant diagnostics.

## 10. Research Director Observability

Research observability should make it possible to determine:

- active campaigns;
- active questions;
- current Research Plan;
- waiting dependencies;
- unresolved contradictions;
- missing capabilities;
- convergence state;
- reason for next-question generation;
- current resource/iteration consumption.

## 11. Decision Observability

Decision observability should make it possible to determine:

- candidate evaluated;
- decision timestamp;
- freshness status;
- result;
- direction;
- implementation type;
- knowledge/SoK version references;
- policy references;
- reason for `NO_ACTION` or `RESEARCH_REQUIRED`;
- expiration/invalidation status.

The full governed Decision artifact remains canonical.

## 12. Learning Observability

Learning & Governance observability should expose:

- evaluation work in progress;
- completed evaluations;
- instability/drift signals;
- recommendations;
- approval status;
- effective-time changes;
- rollback state where applicable.

## 13. Research Nexus Observability

Research Nexus observability should support visibility into:

- publication success/failure;
- retrieval latency;
- integrity failures;
- storage health;
- backup status;
- cache pressure;
- lifecycle transitions;
- archive/delete actions;
- unresolved publication errors.

## 14. Publication Visibility

A durable publication should expose whether it has completed:

```text
identity validation
schema validation
metadata validation
content write
registry/catalog registration
post-write verification
```

Partial publication must not appear as completed publication.

## 15. Metrics

MTS may collect metrics such as:

- task throughput;
- queue depth;
- task latency;
- execution duration;
- retry rate;
- failure rate;
- worker utilization;
- CPU/memory use;
- Nexus read/write latency;
- provider latency;
- cache hit rate;
- publication count;
- Decision latency;
- Research iteration count.

Metrics are observational, not canonical scientific evidence unless explicitly promoted through governed research.

## 16. Health

Components should expose health states appropriate to their role.

Illustrative values:

```text
HEALTHY
DEGRADED
UNAVAILABLE
STARTING
STOPPING
UNKNOWN
```

Exact vocabulary belongs in schemas.

## 17. Liveness vs Readiness

MTS should distinguish:

```text
LIVENESS
```

from:

```text
READINESS
```

A process may be alive but not ready to accept work.

Examples:

- Nexus mounted but failing integrity checks;
- worker running but missing provider credentials;
- Decision worker running but current-state source stale.

## 18. Storage Health

A mounted filesystem does not establish healthy storage.

Storage observability should be able to expose:

- mount/connection state;
- capacity;
- filesystem/backend health;
- read/write failures;
- integrity failures;
- backup status;
- latency anomalies.

## 19. Provider Health

External provider health may include:

- connectivity;
- response latency;
- rate-limit state;
- authentication failure;
- schema change detection;
- stale-feed detection;
- partial coverage.

Provider failure must remain distinguishable from scientific insufficiency.

## 20. Freshness Monitoring

Live/current-state data must expose freshness where material.

Monitoring should detect:

- stale feed;
- missing update;
- delayed event;
- clock skew;
- unexpected observation gaps.

## 21. Clock Integrity

Observability timestamps must use governed time semantics.

MTS should be able to identify:

- event time;
- processing time;
- publication time;

where these differ materially.

## 22. Alerts

Alerts should be generated for conditions that require action or materially threaten system validity.

Examples:

- Research Nexus unavailable;
- backup verification failed;
- storage nearing governed threshold;
- live feed stale;
- repeated worker crash;
- task deadline at risk;
- schema incompatibility;
- integrity failure;
- unauthorized action attempt;
- critical Decision dependency missing.

## 23. Alert Severity

Alert severity should be governed.

Illustrative classes:

```text
INFO
WARNING
ERROR
CRITICAL
```

Severity must represent operational impact rather than developer preference.

## 24. Alert Deduplication

Repeated identical conditions should not produce uncontrolled notification floods.

Alert systems should support:

- deduplication;
- suppression windows;
- escalation;
- resolution state.

Critical distinct events must still remain individually auditable where required.

## 25. Human Operator View

The Control Center should eventually surface:

- system health;
- queue/work status;
- engine status;
- current failures;
- active research;
- Decision activity;
- Nexus status;
- backup status;
- alerts requiring attention.

The UI is a view over governed state and telemetry.

## 26. Audit Record

A material Audit Record should identify:

```text
audit_id
event_type
actor
component
object_ref
action
prior_state where applicable
new_state where applicable
reason
policy_ref
timestamp
execution_ref where applicable
```

Exact schema belongs in Governance/Schemas.

## 27. Audit-Worthy Events

Events requiring durable audit may include:

- knowledge promotion;
- knowledge retirement/supersession;
- policy approval;
- policy change;
- production model promotion;
- Decision creation;
- material task override;
- destructive artifact deletion;
- archive action;
- backup failure affecting permanent data;
- security/authority denial;
- manual intervention in governed workflow;
- rollback.

## 28. Append-Oriented Audit

Audit history should be append-oriented.

Material historical transitions must not be rewritten merely to reflect current state.

Corrections should create new audit entries.

## 29. Actor Identity

Audit records must identify the actor where material.

Actor types may include:

```text
HUMAN
ENGINE
SERVICE
AUTOMATION
SYSTEM
```

Actor identity must be resolvable sufficiently to explain authority.

## 30. Manual Intervention

Manual operator actions that alter governed state must be auditable.

Examples:

- force retry;
- cancel task;
- override priority;
- approve promotion;
- authorize deletion;
- change active model/policy;
- trigger rollback.

## 31. Automated Intervention

Automated actions must be equally auditable.

Automation does not reduce accountability requirements.

## 32. Audit and Provenance

Audit and provenance are related but distinct.

Provenance answers:

> What produced this artifact?

Audit answers:

> What governed action or state transition occurred, by whom/what, and why?

Material workflows may require both.

## 33. Audit and Logs

A log message may support diagnosis of an auditable event.

The durable audit record must not depend on long-term retention of the log stream.

## 34. Retention Classification

Operational logs and metrics are generally:

```text
Class III
```

unless required for durable material audit/provenance.

Audit records associated with material governed events are:

```text
Class II
```

Retention follows `STORAGE_RETENTION_STANDARD.md`.

## 35. Log Retention

Operational log retention should be bounded.

Retention may be based on:

- time;
- volume;
- diagnostic value;
- resource limits.

Logs must not grow indefinitely simply because deletion was never designed.

## 36. Metrics Retention

High-resolution metrics may be downsampled or retired over time.

Long-term summaries may be retained where useful for capacity/performance analysis.

## 37. Audit Retention

Material audit history must be retained according to the lifecycle and significance of the governed event.

Audit records necessary to reconstruct permanent Decisions, policy state, or knowledge lifecycle are normally durable.

## 38. Sensitive Data

Logs, metrics, traces, and audit records must avoid unnecessary inclusion of:

- secrets;
- credentials;
- private keys;
- full provider tokens;
- sensitive external payloads.

Security policy governs redaction requirements.

## 39. Error Reporting

Errors should preserve enough context to diagnose failure.

A useful error record may include:

```text
error_type
component
task_id
execution_id
operation
affected_ref
retryable
message
cause/context
```

Stack traces may be retained transiently where useful.

## 40. Error Taxonomy

MTS should distinguish:

- configuration error;
- schema/contract error;
- provider error;
- storage error;
- integrity error;
- timeout;
- worker loss;
- authorization error;
- domain semantic result.

Domain results such as `NO_ACTION` are not errors.

## 41. Performance Baselines

MTS may establish operational baselines for:

- task latency;
- provider latency;
- storage latency;
- memory use;
- Decision response time;
- queue depth.

Deviation may generate observability signals.

## 42. Capacity Monitoring

MTS should monitor:

- primary Nexus capacity;
- backup capacity;
- cache capacity;
- growth rate;
- log growth;
- database/index growth.

Capacity pressure must not trigger uncontrolled deletion of governed Class II state.

## 43. Research Growth Monitoring

The system should be able to observe growth of:

- active research state;
- historical lineage;
- knowledge artifacts;
- contradiction working sets;
- cache materializations.

This supports the default-to-expire contradiction and retention model.

## 44. Cache Monitoring

Cache observability may include:

- size;
- age distribution;
- hit rate;
- active dependencies;
- retirement backlog.

Cache pressure must not silently promote cache content to canonical status.

## 45. Backup Observability

Backup observability should expose:

- last successful backup;
- last verified backup;
- failed backup;
- backup lag;
- destination health;
- restore-test status where applicable.

## 46. Recovery Observability

After restart/recovery, MTS should report:

- recovered tasks;
- lost executions;
- retried work;
- unresolved orphaned executions;
- Nexus recovery state;
- any state requiring operator attention.

## 47. Version Visibility

Operational status should expose relevant:

- software commit/version;
- interface version;
- schema compatibility;
- effective configuration;
- active model/policy versions where material.

## 48. Environment Visibility

Telemetry must identify environment context such as:

```text
development
test
staging
production
```

to prevent test/development activity from being mistaken for live authoritative behavior.

## 49. Test Observability

Tests should verify observability behavior, including:

- required identifiers;
- error classification;
- audit emission;
- no secret leakage;
- task traceability;
- restart visibility.

## 50. Observability Failure

Failure of noncritical telemetry must not necessarily stop scientific work.

Failure of required audit/provenance recording may be a blocking condition for material operations.

The distinction must be policy-controlled.

## 51. No Silent Audit Loss

If an operation requires durable audit and the audit record cannot be persisted, MTS must not silently report the governed action as fully successful.

## 52. External Monitoring

Future deployments may export telemetry to external monitoring platforms.

External systems are observability tools, not canonical MTS systems of record.

## 53. Vendor Independence

Canonical event semantics should remain independent of a specific logging/metrics vendor.

Changing observability technology must not require rewriting engine domain logic.

## 54. Initial v2 Implementation

The first implementation should support:

1. structured logging;
2. task/execution correlation;
3. engine/worker health;
4. Task Manager queue/status metrics;
5. Nexus publication and storage-health status;
6. machine-readable material audit records;
7. alert generation for critical infrastructure failures;
8. bounded log retention;
9. Control Center-readable status interfaces;
10. restart/recovery diagnostics.

## 55. Initial Proof

A valid observability proof should demonstrate:

```text
submit task
→ task visible as READY
→ assigned worker visible
→ execution correlation visible
→ artifact publication visible
→ task terminal state visible
→ durable audit record exists for any material governed transition
```

Then intentionally fail an execution and prove the failure is diagnosable without parsing private engine files.

## 56. Testing Requirements

Tests should include:

- structured log format;
- task correlation;
- engine health;
- provider failure;
- Nexus failure;
- stale feed;
- backup failure;
- alert creation/resolution;
- audit append behavior;
- manual override audit;
- unauthorized action audit;
- secret redaction;
- restart/recovery visibility;
- log retention/rotation.

## 57. Prohibited Practices

The following are prohibited:

- using logs as canonical task state;
- relying on console text as a machine interface;
- unbounded log growth;
- hiding material failures;
- silently dropping required audit events;
- emitting secrets into telemetry;
- treating liveness as readiness;
- equating a mounted filesystem with healthy storage;
- telemetry formats that require every engine to implement incompatible conventions;
- external monitoring systems becoming alternate systems of record.

## 58. Conformance

A component conforms when it:

1. emits structured observable status;
2. uses canonical correlation identifiers;
3. distinguishes observability from durable audit;
4. keeps canonical domain state out of logs;
5. exposes health/readiness appropriate to its role;
6. supports failure diagnosis;
7. preserves required audit history;
8. respects retention classes;
9. avoids sensitive-data leakage;
10. supports current and future Control Center visibility;
11. remains monitoring-vendor independent.

## 59. Companion Governance

This standard operates with:

```text
ARTIFACT_GOVERNANCE_STANDARD.md
STORAGE_RETENTION_STANDARD.md
ENGINE_INTERFACE_STANDARD.md
TASK_MANAGEMENT_STANDARD.md
CONFIGURATION_STANDARD.md
TEST_AND_VALIDATION_STANDARD.md
CODING_STANDARD.md
SECURITY_AND_AUTHORITY_STANDARD.md
```

and applicable Contracts, Schemas, and Policies.

## 60. Closing Principle

MTS must always be able to answer:

> **What is happening, what failed, what produced this state, what materially changed, who or what caused the change, and what durable record proves it?**

If answering those questions requires reconstructing history from terminal output, observability and audit are not sufficiently governed.
